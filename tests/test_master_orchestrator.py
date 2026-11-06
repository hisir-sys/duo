import json

import pytest

import provider_registry
from orchestrator.master import MasterOrchestrator, validate_master_plan


def task(task_id, *, deps=None, role="coding", provider="gemini"):
    return {
        "id": task_id,
        "title": f"Task {task_id}",
        "role": role,
        "provider": provider,
        "instructions": "Complete this bounded task.",
        "depends_on": deps or [],
        "acceptance_criteria": ["The expected result is verified."],
        "files": [],
    }


def test_master_plan_builds_parallel_stages_and_dependencies():
    payload = [
        task("inspect"),
        task("implement", deps=["inspect"]),
        task("test", deps=["implement"], role="testing"),
        task("review", deps=["implement"], role="review"),
    ]
    plan = validate_master_plan(payload, goal="Build a feature", provider="gemini")
    assert plan.stages == (("inspect",), ("implement",), ("review", "test"))
    assert plan.tasks[0].provider == "gemini"
    assert plan.as_dict()["master_provider"] == "gemini"


@pytest.mark.parametrize("payload", [
    [],
    [task("one")] * 13,
    [task("one"), task("one")],
    [task("one", deps=["missing"])],
    [task("one", deps=["one"])],
    [task("one", deps=["two"]), task("two", deps=["one"])],
    [task("one", role="random")],
    [task("one", provider="made-up")],
    [{**task("one"), "acceptance_criteria": []}],
])
def test_master_plan_rejects_invalid_or_unsafe_structure(payload):
    with pytest.raises(ValueError):
        validate_master_plan(payload, goal="Build a feature", provider="gemini")


def test_master_plan_rejects_unknown_top_level_provider():
    with pytest.raises(ValueError):
        validate_master_plan([task("one")], goal="Build a feature", provider="made-up")


def test_master_orchestrator_asks_selected_master_provider_and_validates():
    seen = {}
    response = json.dumps([task("inspect"), task("build", deps=["inspect"])])
    def fake_ask(provider, system, prompt, attachments, cfg):
        seen.update(provider=provider, system=system, prompt=prompt, attachments=attachments)
        return response

    master = MasterOrchestrator(fake_ask, provider_names=["gemini", "groq"])
    plan = master.create_plan("Build a safe feature", provider="gemini", cfg={},
                              project_context="Python desktop application")
    assert seen["provider"] == "gemini"
    assert "Available providers: gemini, groq" in seen["system"]
    assert plan.stages == (("inspect",), ("build",))


def test_master_orchestrator_rejects_unconfigured_task_provider():
    response = json.dumps([task("inspect", provider="cerebras")])
    master = MasterOrchestrator(lambda *args: response, provider_names=["gemini"])
    with pytest.raises(ValueError, match="unconfigured"):
        master.create_plan("Build a feature", provider="gemini", cfg={})


def test_master_orchestrator_rejects_invalid_json():
    master = MasterOrchestrator(lambda *args: "not json", provider_names=["gemini"])
    with pytest.raises(ValueError, match="invalid JSON"):
        master.create_plan("Build a feature", provider="gemini", cfg={})


def test_master_requires_at_least_one_provider():
    with pytest.raises(ValueError):
        MasterOrchestrator(lambda *args: "[]", provider_names=[])



def test_master_orchestrator_accepts_fenced_json():
    response = "Here is the plan:\n```json\n" + json.dumps([task("inspect")]) + "\n```"
    master = MasterOrchestrator(lambda *args: response, provider_names=["gemini"])
    plan = master.create_plan("Inspect the project", provider="gemini", cfg={})
    assert plan.tasks[0].id == "inspect"
