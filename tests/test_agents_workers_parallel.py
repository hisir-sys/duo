from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from time import sleep
from types import SimpleNamespace

from agents.workers import MasterWorkerTeam


def make_task(task_id, *, role="research", depends_on=()):
    return SimpleNamespace(
        id=task_id,
        title=f"Task {task_id}",
        role=role,
        provider="gemini",
        instructions="Complete this task.",
        depends_on=tuple(depends_on),
        acceptance_criteria=("The result is complete.",),
        files=(),
    )


def make_plan(tasks, stages):
    return SimpleNamespace(
        goal="Build a tested feature",
        tasks=tuple(tasks),
        stages=tuple(tuple(stage) for stage in stages),
    )


def test_independent_tasks_run_in_parallel_and_checkpoint(tmp_path):
    lock = Lock()
    active = 0
    peak = 0

    def ask(provider, system, prompt, attachments, cfg):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        sleep(0.12)
        with lock:
            active -= 1
        return "Completed."

    plan = make_plan(
        [make_task("one"), make_task("two"), make_task("three")],
        [("one", "two", "three")],
    )
    result = MasterWorkerTeam(ask, tmp_path).run(plan, cfg={}, max_parallel=2)

    assert peak == 2
    assert result["status"] == "completed"
    assert result["completed"] == 3
    assert result["pending"] == 0
    assert result["source_project_modified"] is False
    assert result["commands_executed"] is False
    saved = (Path(result["workspace"]) / "run.json").read_text("utf-8")
    assert '"status": "completed"' in saved


def test_worker_retries_once_and_records_attempt_count(tmp_path):
    calls = 0

    def ask(provider, system, prompt, attachments, cfg):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("Temporary provider failure")
        return "Recovered."

    plan = make_plan([make_task("retry")], [("retry",)])
    result = MasterWorkerTeam(ask, tmp_path).run(plan, cfg={})

    assert calls == 2
    assert result["completed"] == 1
    assert result["attempts"] == {"retry": 2}


def test_failed_dependency_blocks_downstream_task(tmp_path):
    def ask(provider, system, prompt, attachments, cfg):
        raise RuntimeError("Provider unavailable")

    plan = make_plan(
        [make_task("first"), make_task("second", depends_on=("first",))],
        [("first",), ("second",)],
    )
    result = MasterWorkerTeam(ask, tmp_path).run(plan, cfg={})

    assert result["failed"] == 1
    assert result["blocked"] == 1
    assert result["pending"] == 0
    statuses = {item["task_id"]: item["status"] for item in result["results"]}
    assert statuses == {"first": "failed", "second": "blocked"}


def test_parallelism_limit_is_validated(tmp_path):
    plan = make_plan([make_task("one")], [("one",)])
    team = MasterWorkerTeam(lambda *args: "Completed.", tmp_path)

    for invalid in (0, 13, True, 1.5):
        try:
            team.run(plan, cfg={}, max_parallel=invalid)
        except ValueError as error:
            assert "between 1 and 12" in str(error)
        else:
            raise AssertionError(f"Expected invalid parallelism {invalid!r} to fail")
