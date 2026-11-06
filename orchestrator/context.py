"""Read-only, bounded project context collection for the Master Orchestrator."""
from pathlib import Path

MAX_FILES = 120
MAX_TOTAL_CHARS = 16000
MAX_FILE_CHARS = 3000
IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", "target", ".idea", ".vscode",
}
SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.production", "secrets.json",
    "credentials.json", "key.json", "keys.json", "id_rsa", "id_ed25519",
}
TEXT_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".json", ".toml",
    ".yaml", ".yml", ".md", ".rst", ".txt", ".ini", ".cfg", ".css",
    ".html", ".xml", ".sql", ".sh", ".bat", ".ps1", ".cs", ".cpp",
    ".h", ".java", ".go", ".rs", ".swift", ".kt", ".dart",
}


def inspect_project(root) -> str:
    """Return a bounded file tree and selected text files; never execute or modify files."""
    base = Path(root).expanduser().resolve(strict=True)
    if not base.is_dir():
        raise ValueError("The selected project path must be a directory.")

    lines = [f"Project root: {base.name}", "File inventory:"]
    selected = []
    count = 0
    total_chars = 0

    for current, dirs, files in __import__("os").walk(base, followlinks=False):
        current_path = Path(current)
        dirs[:] = sorted(
            name for name in dirs
            if name not in IGNORED_DIRS
            and not (current_path / name).is_symlink()
        )
        for filename in sorted(files):
            path = current_path / filename
            if path.is_symlink() or filename.casefold() in SENSITIVE_NAMES:
                continue
            if filename.startswith(".env.") or filename.endswith((".pem", ".key", ".p12", ".pfx")):
                continue
            try:
                relative = path.relative_to(base).as_posix()
                size = path.stat().st_size
            except (OSError, ValueError):
                continue
            if size > 2_000_000:
                continue
            lines.append(f"- {relative} ({size} bytes)")
            count += 1
            if path.suffix.lower() not in TEXT_SUFFIXES or total_chars >= MAX_TOTAL_CHARS:
                continue
            try:
                text = path.read_text("utf-8")
            except (OSError, UnicodeError):
                continue
            remaining = MAX_TOTAL_CHARS - total_chars
            snippet = text[:min(MAX_FILE_CHARS, remaining)]
            if not snippet:
                continue
            selected.append(f"\n--- {relative} ---\n{snippet}")
            total_chars += len(snippet)
            if count >= MAX_FILES or total_chars >= MAX_TOTAL_CHARS:
                break
        if count >= MAX_FILES or total_chars >= MAX_TOTAL_CHARS:
            break

    if count == 0:
        lines.append("(No readable project files found.)")
    lines.append(f"\nIncluded text excerpts: {len(selected)}")
    return ("\n".join(lines) + "".join(selected))[:20000]
