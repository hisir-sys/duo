"""Master Orchestrator planning and dependency validation.

This module plans work only. Worker execution and workspace integration are
intentionally handled by later phases.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping

import provider_registry

ROLES = {"coding", "testing", "review", "research"}
MAX_TASKS = 12
MAX_TITLE = 160
MAX_INSTRUCTIONS = 12000


@dataclass(frozen=True)
class PlannedTask:
    id: str
    title: str
    role: str
    provider: str
    instructions: str
    depends_on: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    files: tuple[str, ...]


@dataclass(frozen=True)
class MasterPlan:
    goal: str
    provider: str
    tasks: tuple[PlannedTask, ...]
    stages: tuple[tuple[str, ...], ...]

    def as_dict(self) -> dict:
        return {
            "goal": self.goal,
            "master_provider": self.provider,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "role": task.role,
                    "provider": task.provider,
                    "instructions": task.instructions,
                    "depends_on": list(task.depends_on),
                    "acceptance_criteria": list(task.acceptance_criteria),
                    "files": list(task.files),
                }
                for task in self.tasks
            ],
            "stages": [list(stage) for stage in self.stages],
        }


def _short_text(value, field: str, limit: int, *, required: bool = True) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text.")
    value = value.strip()
    if required and not value:
        raise ValueError(f"{field} cannot be empty.")
    if len(value) > limit:
        raise ValueError(f"{field} exceeds {limit} characters.")
    return value


def _string_list(value, field: str, *, limit: int, item_limit: int,
                 required: bool = False) -> tuple[str, ...]:
    if value is None and not required:
        return ()
    if not isinstance(value, list) or len(value) > limit:
        raise ValueError(f"{field} must be a list of at most {limit} items.")
    result = tuple(_short_text(item, field, item_limit) for item in value)
    if required and not result:
        raise ValueError(f"{field} must contain at least one item.")
    return result


def _topological_stages(tasks: tuple[PlannedTask, ...]) -> tuple[tuple[str, ...], ...]:
    by_id = {task.id: task for task in tasks}
    remaining = {task.id: set(task.depends_on) for task in tasks}
    stages = []
    completed = set()

    while len(completed) < len(tasks):
        ready = sorted(task_id for task_id, deps in remaining.items()
                       if task_id not in completed and deps.issubset(completed))
        if not ready:
            raise ValueError("Task dependencies contain a cycle.")
        stages.append(tuple(ready))
        completed.update(ready)
    return tuple(stages)


def validate_master_plan(payload, *, goal: str, provider: str) -> MasterPlan:
    if not isinstance(payload, list) or not 1 <= len(payload) <= MAX_TASKS:
        raise ValueError(f"The Master must return 1–{MAX_TASKS} tasks.")

    tasks = []
    seen = set()
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict):
            raise ValueError(f"Task {index} must be an object.")
        task_id = _short_text(item.get("id"), f"Task {index} id", 32)
        if not task_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"Task {index} id contains unsupported characters.")
        if task_id in seen:
            raise ValueError(f"Duplicate task id: {task_id}.")
        seen.add(task_id)

        role = _short_text(item.get("role"), f"Task {index} role", 20).lower()
        if role not in ROLES:
            raise ValueError(f"Task {index} has unsupported role '{role}'.")
        task_provider = _short_text(item.get("provider"), f"Task {index} provider", 32).lower()
        provider_registry.get_spec(task_provider)

        tasks.append(PlannedTask(
            id=task_id,
            title=_short_text(item.get("title"), f"Task {index} title", MAX_TITLE),
            role=role,
            provider=task_provider,
            instructions=_short_text(item.get("instructions"), f"Task {index} instructions", MAX_INSTRUCTIONS),
            depends_on=_string_list(item.get("depends_on", []), f"Task {index} dependencies",
                                    limit=MAX_TASKS, item_limit=32),
            acceptance_criteria=_string_list(item.get("acceptance_criteria", []),
                                              f"Task {index} acceptance criteria",
                                              limit=10, item_limit=500, required=True),
            files=_string_list(item.get("files", []), f"Task {index} files",
                               limit=50, item_limit=300),
        ))

    for task in tasks:
        for dependency in task.depends_on:
            if dependency not in seen:
                raise ValueError(f"Task '{task.id}' depends on unknown task '{dependency}'.")
            if dependency == task.id:
                raise ValueError(f"Task '{task.id}' cannot depend on itself.")

    stages = _topological_stages(tuple(tasks))
    return MasterPlan(
        goal=_short_text(goal, "Project goal", 12000),
        provider=provider_registry.get_spec(provider) and provider,
        tasks=tuple(tasks),
        stages=stages,
    )


class MasterOrchestrator:
    """Turn a project request into a validated, dependency-aware work plan."""

    def __init__(self, ask_fn: Callable, *, provider_names: Iterable[str]):
        self.ask_fn = ask_fn
        self.provider_names = tuple(dict.fromkeys(provider_names))
        if not self.provider_names:
            raise ValueError("At least one configured provider is required.")
        for name in self.provider_names:
            provider_registry.get_spec(name)

    def create_plan(self, goal: str, *, provider: str, cfg: Mapping,
                    project_context: str = "") -> MasterPlan:
        provider_registry.get_spec(provider)
        goal = _short_text(goal, "Project goal", 12000)
        context = _short_text(project_context, "Project context", 20000, required=False)
        system = (
            "You are the Master Orchestrator of DuoAI Studio. You plan software work; "
            "you do not claim to have executed code or inspected files that were not supplied. "
            "Break the user's goal into small, non-overlapping tasks. Identify dependencies, "
            "roles, concrete acceptance criteria, and likely files only when grounded in context. "
            "Use only the listed providers. Prefer coding, testing, and independent review tasks. "
            "Return ONLY a JSON array. Each object must contain: id, title, role, provider, "
            "instructions, depends_on (array of task IDs), acceptance_criteria (non-empty array), "
            "files (array, may be empty). No markdown fences or commentary.\n\n"
            f"Available providers: {', '.join(self.provider_names)}"
        )
        prompt = f"Project goal:\n{goal}\n\nProject context supplied by the user/app:\n{context or '(none)'}"
        output = self.ask_fn(provider, system, prompt, [], cfg)
        import json
        try:
            payload = json.loads(output.strip())
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("The Master returned invalid JSON. Please retry.") from exc
        plan = validate_master_plan(payload, goal=goal, provider=provider)
        invalid = [task.provider for task in plan.tasks if task.provider not in self.provider_names]
        if invalid:
            raise ValueError("The Master assigned a task to an unconfigured provider.")
        return plan
