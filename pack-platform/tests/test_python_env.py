"""Backend Python / venv resolution."""

from __future__ import annotations

from pathlib import Path

from pack.util.python_env import resolve_backend_python


def test_resolve_prefers_venv(tmp_path: Path) -> None:
    if __import__("os").name == "nt":
        py = tmp_path / ".venv" / "Scripts" / "python.exe"
    else:
        py = tmp_path / ".venv" / "bin" / "python"
    py.parent.mkdir(parents=True)
    py.write_bytes(b"MZ")
    found = resolve_backend_python(tmp_path)
    assert found == py.resolve()
