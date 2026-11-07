import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agents.workers import MasterWorkerTeam, WorkerAgent, _safe_artifact_path
from orchestrator.master import PlannedTask, MasterPlan


def planned(task_id, role="coding", deps=(), provider="gemini"):
    return PlannedTask(
        id=task_id, title=f"{role.title()} {task_id}", role=role, provider=provider,
        instructions="Complete the bounded task.", depends_on=tuple(deps),
        acceptance_criteria=("The result meets the requirement.",), files=("src/example.py",),
    )


def plan(*tasks):
    stages = tuple((task.id,) for task in tasks)
    return MasterPlan("Build a feature", "gemini", tuple(tasks), stages)


def test_team_uses_separate_workspaces_and_saves_coding_proposals(tmp_path):
    calls = []
    def ask(provider, system, prompt, attachments, cfg):
        calls.append((provider, system, prompt))
        if "You are the Coding Agent." in system:
            return "Proposed file:\n```python path=src/example.py\nprint('proposal')\n```"
        return "Independent review complete."

    team = MasterWorkerTeam(ask, tmp_path / "workspaces")
    result = team.run(plan(planned("code"), planned("review", "review", ("code",))),
                      cfg={}, project_id="1234abcd", project_context="read-only context")
    first, second = result["results"]
    assert result["completed"] == 2
    assert first["workspace"] != second["workspace"]
    assert first["artifacts"] == ("proposals/src/example.py",)
    proposed = Path(first["workspace"]) / "proposals" / "src" / "example.py"
    assert proposed.read_text() == "print('proposal')"
    assert "Independent review complete." in second["output"]
    assert "read-only context" in calls[0][2]
    assert result["source_project_modified"] is False
    assert result["commands_executed"] is False


def test_failed_worker_blocks_dependent_but_not_independent_task(tmp_path):
    def ask(provider, system, prompt, attachments, cfg):
        if "Coding Agent" in system:
            raise RuntimeError("provider unavailable")
        return "Done."

    tasks = (planned("code"), planned("dependent", "review", ("code",)),
             planned("independent", "testing"))
    # Independent tasks are placed in the same stage; dependent follows.
    p = MasterPlan("Goal", "gemini", tasks, (("code", "independent"), ("dependent",)))
    result = MasterWorkerTeam(ask, tmp_path).run(p, cfg={})
    statuses = {item["task_id"]: item["status"] for item in result["results"]}
    assert statuses == {"code": "failed", "dependent": "blocked", "independent": "completed"}


@pytest.mark.parametrize("path", ["../outside.py", "/absolute.py", "C:/outside.py", ""])
def test_artifact_path_rejects_escape(tmp_path, path):
    with pytest.raises(ValueError):
        _safe_artifact_path(tmp_path, path)


def test_worker_rejects_empty_response():
    task = planned("code")
    agent = WorkerAgent("coding", lambda *args: " ")
    with pytest.raises(ValueError, match="empty"):
        agent.run(task, goal="Goal", provider="gemini", cfg={}, project_context="",
                  prior_results=(), workspace=Path("unused"))


def test_team_rejects_invalid_project_id(tmp_path):
    with pytest.raises(ValueError, match="project identifier"):
        MasterWorkerTeam(lambda *args: "Done", tmp_path).run(plan(planned("code")),
                                                               cfg={}, project_id="../outside")
