import importlib.util
from pathlib import Path

import pytest

BRIDGE_PATH = Path(__file__).parents[1] / "desktop-ui" / "electron" / "backend_bridge.py"
SPEC = importlib.util.spec_from_file_location("duo_electron_backend_bridge", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


def test_health_reports_core_without_exposing_credentials(monkeypatch):
    monkeypatch.setattr(bridge, "_provider_state", lambda: [
        {"id": "gemini", "connected": True, "model": "gemini-test"}
    ])
    result = bridge.dispatch("health", {})
    assert result["ok"] is True
    assert result["backend"] == "python-core"
    assert "api_key" not in result
    assert "secret" not in str(result).lower()


def test_projects_list_uses_existing_core_storage(monkeypatch):
    expected = [{"id": "1234abcd", "name": "Test project", "tasks": [], "log": []}]
    monkeypatch.setattr(bridge.core, "list_projects", lambda: expected)
    assert bridge.dispatch("projects.list", {}) == {"projects": expected}


def test_projects_create_validates_name(monkeypatch):
    monkeypatch.setattr(bridge.core, "new_project", lambda name: {"id": "1234abcd", "name": name})
    assert bridge.dispatch("projects.create", {"name": "Bridge test"})["project"]["name"] == "Bridge test"
    with pytest.raises(ValueError):
        bridge.dispatch("projects.create", {"name": "   "})


def test_provider_operations_reject_unknown_provider():
    with pytest.raises(ValueError, match="Unsupported provider"):
        bridge.dispatch("providers.test", {"provider": "unknown"})


def test_master_run_requires_a_plan():
    with pytest.raises(ValueError, match="Master plan"):
        bridge.dispatch("master.run", {})


def test_unknown_operations_are_rejected():
    with pytest.raises(ValueError, match="Unsupported backend operation"):
        bridge.dispatch("os.execute", {"command": "not allowed"})
