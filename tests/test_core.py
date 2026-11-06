import json
from pathlib import Path

import pytest
import core


def test_atomic_save_round_trips_json(tmp_path, monkeypatch):
    target = tmp_path / "nested" / "config.json"
    core._save(target, {"name": "DuoAI", "enabled": True})
    assert json.loads(target.read_text("utf-8")) == {"name": "DuoAI", "enabled": True}
    assert list(target.parent.glob("*.tmp")) == []


def test_parse_json_from_fenced_response():
    raw = 'Here is the plan:\n\x60\x60\x60json\n[{"title":"Build","assignee":"claude","instructions":"Implement it"},{"title":"Test","assignee":"chatgpt","instructions":"Test it"}]\n\x60\x60\x60'
    assert len(core.parse_json_payload(raw)) == 2


def test_parse_json_rejects_invalid_output():
    with pytest.raises(ValueError):
        core.parse_json_payload("No JSON was returned")


def test_validate_plan_normalizes_provider():
    result = core.validate_plan([
        {"title": "Build", "assignee": "claude", "instructions": "Implement the feature"},
        {"title": "Review", "assignee": "openai", "instructions": "Review the feature"},
    ])
    assert result[1]["assignee"] == "chatgpt"
    assert result[0]["output"] == ""


@pytest.mark.parametrize("payload", [
    [],
    [{"title": "", "assignee": "claude", "instructions": "x"}, {"title": "B", "assignee": "claude", "instructions": "y"}],
    [{"title": "A", "assignee": "unknown", "instructions": "x"}, {"title": "B", "assignee": "claude", "instructions": "y"}],
    [{"title": "A", "assignee": "claude", "instructions": ""}, {"title": "B", "assignee": "claude", "instructions": "y"}],
])
def test_validate_plan_rejects_bad_tasks(payload):
    with pytest.raises(ValueError):
        core.validate_plan(payload)


def test_memory_write_is_atomic_and_size_limited(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "MEM", tmp_path / "memory.md")
    core.set_mem("# Shared memory\n")
    assert core.get_mem() == "# Shared memory\n"
    with pytest.raises(ValueError):
        core.set_mem("x" * 100001)


def test_safe_export_path_rejects_traversal():
    with pytest.raises(ValueError):
        core.safe_export_path("1234abcd", "../outside.txt")


def test_safe_export_path_accepts_relative_file(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "WORK", tmp_path)
    result = core.safe_export_path("1234abcd", "src/main.py")
    assert result == (tmp_path / "1234abcd" / "src" / "main.py").resolve()


def test_plaintext_legacy_key_is_not_used(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "KEYS", tmp_path / "keys.json")
    monkeypatch.setattr(core.os, "environ", {})
    (tmp_path / "keys.json").write_text('{"claude":"plaintext-secret"}', encoding="utf-8")
    class DisabledKeyring:
        @staticmethod
        def get_keyring():
            class Backend:
                priority = 0
            return Backend()
    monkeypatch.setitem(__import__("sys").modules, "keyring", DisabledKeyring)
    assert core.get_key("claude") is None
