"""Installer packagers and source-leak verification tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from pack.context import BuildContext
from pack.models import (
    BackendSpec,
    FrontendSpec,
    PackManifest,
    PackSpec,
    PackTarget,
    PackageFormat,
    ProductSpec,
    SecuritySpec,
    ShellKind,
    TargetArch,
    TargetOS,
)
from pack.packagers.inno import InnoPackager
from pack.pipeline.runner import platform_root
from pack.pipeline.verify import VerifyError, run_verify_assemble
from pack.shells.headless import HeadlessShellAssembler


def _manifest(*, fmt: PackageFormat) -> PackManifest:
    return PackManifest(
        product=ProductSpec(
            name="innoapp",
            version="1.0.0",
            appId="com.inno",
            displayName="Inno App",
            vendor="Test",
        ),
        frontend=FrontendSpec(dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(adapter="python-nuitka", dir="backend", entry="scripts/run_portable.py"),
        security=SecuritySpec(compile=True, sbom=False, checksums=False),
        pack=PackSpec(
            output_dir="dist/pack",
            targets=[
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=ShellKind.HEADLESS,
                    format=fmt,
                )
            ],
        ),
    )


def _seed_artifacts(ctx: BuildContext) -> None:
    fe = ctx.artifacts_dir / "frontend" / "dist"
    fe.mkdir(parents=True)
    (fe / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    (fe / "app.js").write_text("console.log(1)", encoding="utf-8")
    be = ctx.artifacts_dir / "backend" / "run_portable"
    be.mkdir(parents=True)
    (be / "run_portable.exe").write_bytes(b"MZ")


def test_inno_emits_iss_script(tmp_path: Path) -> None:
    project = tmp_path / "app"
    project.mkdir()
    manifest = _manifest(fmt=PackageFormat.INNO)
    manifest.product.installer.file_name = "NTesterc-1.0.0"
    # No product.installer.icon — must use pack-platform/branding/app-icon.png
    ctx = BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=manifest,
        target=manifest.pack.targets[0],
        skip_frontend=True,
        skip_backend=True,
    )
    ctx.output_dir = tmp_path / "out"
    ctx.output_dir.mkdir(parents=True, exist_ok=True)
    _seed_artifacts(ctx)

    assemble = HeadlessShellAssembler().assemble(ctx)
    final = InnoPackager().package(ctx, assemble)
    inno_dir = ctx.output_dir / f"{ctx.artifact_name}.inno"
    iss = inno_dir / "setup.iss"
    assert iss.is_file()
    text = iss.read_text(encoding="utf-8")
    assert "Inno App" in text
    assert "launch.bat" in text
    assert "brand.ico" in text
    assert "WizardImageFile=" in text
    assert (inno_dir / "setup-icon.ico").is_file()
    assert (inno_dir / "wizard-large.bmp").is_file()
    assert (platform_root() / "branding" / "app-icon.png").is_file()


def test_verify_rejects_py_source_leak(tmp_path: Path) -> None:
    project = tmp_path / "app"
    project.mkdir()
    manifest = _manifest(fmt=PackageFormat.INNO)
    ctx = BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=manifest,
        target=manifest.pack.targets[0],
        skip_frontend=True,
        skip_backend=True,
    )
    _seed_artifacts(ctx)
    HeadlessShellAssembler().assemble(ctx)
    (ctx.assemble_dir / "app" / "leaked.py").write_text("print('secret')\n", encoding="utf-8")

    with pytest.raises(VerifyError, match="customer source files"):
        run_verify_assemble(ctx)


def test_verify_allows_alembic_migration_py(tmp_path: Path) -> None:
    project = tmp_path / "app"
    project.mkdir()
    manifest = _manifest(fmt=PackageFormat.INNO)
    ctx = BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=manifest,
        target=manifest.pack.targets[0],
        skip_frontend=True,
        skip_backend=True,
    )
    _seed_artifacts(ctx)
    HeadlessShellAssembler().assemble(ctx)
    mig = (
        ctx.assemble_dir
        / "runtime"
        / "backend"
        / "data"
        / "alembic"
        / "versions"
        / "001_init.py"
    )
    mig.parent.mkdir(parents=True)
    mig.write_text("revision = '001'\n", encoding="utf-8")

    run_verify_assemble(ctx)


def test_ambiguous_windows_targets_require_selector(tmp_path: Path) -> None:
    manifest = PackManifest(
        product=ProductSpec(name="demo", version="1.0.0", appId="com.demo"),
        frontend=FrontendSpec(dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(adapter="python-nuitka", dir="backend", entry="main.py"),
        pack=PackSpec(
            targets=[
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=ShellKind.HEADLESS,
                    format=PackageFormat.INNO,
                ),
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=ShellKind.HEADLESS,
                    format=PackageFormat.MSI,
                ),
            ]
        ),
    )
    with pytest.raises(KeyError, match="Ambiguous"):
        manifest.find_target("windows-x64-headless")
    assert manifest.find_target("windows-x64-headless-inno").format == PackageFormat.INNO
    assert manifest.find_target("windows-x64-headless-msi").format == PackageFormat.MSI
