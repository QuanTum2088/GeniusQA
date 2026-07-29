"""Unit tests for production gate and launcher resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from pack.models import (
    BackendSpec,
    FrontendSpec,
    PackManifest,
    PackSpec,
    PackTarget,
    PackageFormat,
    ProductSpec,
    ShellKind,
    TargetArch,
    TargetOS,
)
from pack.pipeline.preflight import PRODUCTION_FORMATS, PRODUCTION_SHELLS, ProductionGateError
from pack.util.launcher import find_launcher, launcher_candidates
from pack.util.sbom_deps import _parse_requirements, _parse_uv_lock


def test_production_sets() -> None:
    assert "headless" in PRODUCTION_SHELLS
    assert "zip" in PRODUCTION_FORMATS
    assert "dir" in PRODUCTION_FORMATS
    assert "msi" in PRODUCTION_FORMATS
    assert "inno" in PRODUCTION_FORMATS
    assert "tauri" not in PRODUCTION_SHELLS


def test_launcher_candidates_prefer_normalized(tmp_path: Path) -> None:
    be = tmp_path / "backend"
    stem = "run_portable"
    target = be / stem / f"{stem}.exe"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"MZ")
    found = find_launcher(be, stem)
    assert found == target
    assert launcher_candidates(be, stem)[0].name.endswith((".exe", stem))


def test_parse_requirements(tmp_path: Path) -> None:
    req = tmp_path / "requirements"
    req.write_text("fastapi==0.111.0\n# comment\nuvicorn>=0.31.1\n", encoding="utf-8")
    comps = _parse_requirements(req)
    names = {c["name"] for c in comps}
    assert "fastapi" in names
    assert "uvicorn" in names


def test_parse_uv_lock(tmp_path: Path) -> None:
    lock = tmp_path / "uv.lock"
    lock.write_text(
        'version = 1\n\n[[package]]\nname = "httpx"\nversion = "0.28.1"\n\n'
        '[[package]]\nname = "fastapi"\nversion = "0.111.0"\n',
        encoding="utf-8",
    )
    comps = _parse_uv_lock(lock)
    by_name = {c["name"]: c["version"] for c in comps}
    assert by_name["httpx"] == "0.28.1"
    assert by_name["fastapi"] == "0.111.0"


def test_manifest_target_key() -> None:
    m = PackManifest(
        product=ProductSpec(name="demo", version="1.0.0", appId="com.demo"),
        frontend=FrontendSpec(adapter="vite", dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(adapter="python-nuitka", dir="backend", entry="main.py"),
        pack=PackSpec(
            targets=[
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=ShellKind.HEADLESS,
                    format=PackageFormat.ZIP,
                )
            ]
        ),
    )
    assert m.find_target("windows-x64-headless").format == PackageFormat.ZIP
    with pytest.raises(KeyError):
        m.find_target("windows-x64")
