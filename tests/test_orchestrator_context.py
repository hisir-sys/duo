from pathlib import Path

import pytest

from orchestrator.context import inspect_project


def test_inspect_project_collects_tree_and_text_without_modifying(tmp_path):
    (tmp_path / "src").mkdir()
    source = tmp_path / "src" / "app.py"
    source.write_text("print('hello')\n", encoding="utf-8")
    before = source.read_bytes()
    context = inspect_project(tmp_path)
    assert "src/app.py" in context
    assert "print('hello')" in context
    assert source.read_bytes() == before


def test_inspect_project_excludes_credentials_and_generated_folders(tmp_path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "package.json").write_text("{}", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET=do-not-send", encoding="utf-8")
    (tmp_path / "credentials.json").write_text("secret", encoding="utf-8")
    (tmp_path / "safe.py").write_text("print('safe')", encoding="utf-8")
    context = inspect_project(tmp_path)
    assert "safe.py" in context
    assert "node_modules" not in context
    assert "do-not-send" not in context
    assert "secret" not in context


def test_inspect_project_rejects_non_directory(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("text", encoding="utf-8")
    with pytest.raises(ValueError, match="directory"):
        inspect_project(file_path)


def test_inspect_project_bounds_context_size(tmp_path):
    for index in range(130):
        (tmp_path / f"file_{index:03}.py").write_text("x" * 1000, encoding="utf-8")
    context = inspect_project(tmp_path)
    assert len(context) < 25000
    assert context.count("\n- ") <= 120
