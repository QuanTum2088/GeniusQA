"""Tests for embedded runtime layout."""

from __future__ import annotations

from pathlib import Path

from pack.context import BuildContext
from pack.models import (
    BackendSpec,
    FrontendSpec,
    PackManifest,
    PackSpec,
    PackTarget,
    PackageFormat,
    ProductSpec,
    RuntimeSpec,
    ShellKind,
    TargetArch,
    TargetOS,
)
from pack.pipeline.runner import platform_root
from pack.runtime.embedded import EmbeddedRuntimeProvider


def test_embedded_layout(tmp_path: Path) -> None:
    project = tmp_path / "app"
    project.mkdir()
    manifest = PackManifest(
        product=ProductSpec(name="e", version="1.0.0", appId="com.e"),
        frontend=FrontendSpec(dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(adapter="python-nuitka", dir="backend", entry="main.py"),
        runtime=RuntimeSpec(database="embedded", cache="embedded", provider="embedded"),
        pack=PackSpec(
            output_dir=str(tmp_path / "out"),
            targets=[
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=ShellKind.HEADLESS,
                    format=PackageFormat.DIR,
                )
            ],
        ),
    )
    ctx = BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=manifest,
        target=manifest.pack.targets[0],
    )
    root = tmp_path / "assemble"
    root.mkdir()
    EmbeddedRuntimeProvider().prepare(ctx, root)
    assert (root / "runtime" / "embedded" / "MANIFEST.json").is_file()
    assert (root / "start-embedded.bat").is_file()
    assert (root / "start-embedded.sh").is_file()
    assert (root / "data" / "mysql").is_dir()
    assert (root / "RUNTIME.md").is_file()
