"""Assemble/verify smoke test without Nuitka (fake artifacts)."""

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
    ShellKind,
    TargetArch,
    TargetOS,
)
from pack.pipeline.package import run_package
from pack.pipeline.verify import run_verify_assemble
from pack.pipeline.runner import platform_root
from pack.shells.headless import HeadlessShellAssembler


def _fake_ctx(tmp_path: Path) -> BuildContext:
    project = tmp_path / "app"
    fe = project / "frontend" / "dist"
    be = project / "backend"
    fe.mkdir(parents=True)
    be.mkdir(parents=True)
    (fe / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    (be / "scripts").mkdir(parents=True)
    (be / "scripts" / "run_portable.py").write_text("print('x')\n", encoding="utf-8")
    (project / "config.example.yaml").write_text("server:\n  port: 8100\n", encoding="utf-8")

    manifest = PackManifest(
        product=ProductSpec(name="smoke", version="0.0.1", appId="com.smoke"),
        frontend=FrontendSpec(dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(
            adapter="python-nuitka",
            dir="backend",
            entry="scripts/run_portable.py",
            workers=[],
        ),
        pack=PackSpec(
            output_dir="dist/pack",
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
    # Force output under tmp
    manifest.pack.output_dir = str(tmp_path / "out")

    ctx = BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=manifest,
        target=manifest.pack.targets[0],
        skip_frontend=True,
        skip_backend=True,
    )

    # Seed artifacts as if FE/BE already built
    art_fe = ctx.artifacts_dir / "frontend" / "dist"
    art_fe.mkdir(parents=True)
    (art_fe / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    art_be = ctx.artifacts_dir / "backend" / "run_portable"
    art_be.mkdir(parents=True)
    (art_be / "run_portable.exe").write_bytes(b"MZ")
    (ctx.artifacts_dir / "backend" / "PACK_BACKEND.txt").write_text(
        "adapter=python-nuitka\n", encoding="utf-8"
    )
    return ctx


def test_headless_assemble_verify_package(tmp_path: Path) -> None:
    ctx = _fake_ctx(tmp_path)
    root = HeadlessShellAssembler().assemble(ctx)
    assert (root / "start.bat").is_file()
    assert (root / "first-run.bat").is_file()
    assert (root / "stop.bat").is_file()
    assert (root / "healthcheck.bat").is_file()
    assert (root / "service" / "smoke.service").is_file()
    assert (root / "service" / "install-windows-service.ps1").is_file()
    assert (root / "service" / "smoke.plist").is_file()
    run_verify_assemble(ctx)
    out = run_package(ctx)
    assert out.is_dir()
    assert (out / "VERSION").is_file()
