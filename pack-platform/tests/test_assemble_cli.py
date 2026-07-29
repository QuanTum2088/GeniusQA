"""Tests for pack assemble-only and MSI heat scaffold."""

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
from pack.packagers.msi import MsiPackager
from pack.pipeline.assemble_only import run_assemble_only
from pack.pipeline.runner import platform_root
from pack.shells.headless import HeadlessShellAssembler


_MANIFEST_YAML = """
product:
  name: asm
  version: "0.0.1"
  appId: com.asm
  displayName: Asm
  vendor: Test

frontend:
  adapter: vite
  dir: frontend
  install: echo skip
  build: echo skip
  dist: frontend/dist

backend:
  adapter: python-nuitka
  dir: backend
  entry: scripts/run_portable.py
  python: "3.11"
  workers: []
  packages: []
  collect_all: []
  hiddenimports: []
  excludes: []
  data: []
  healthcheck_url: "http://127.0.0.1:8100/api/health/health"
  nuitka:
    jobs: 0
    include_package_data: true
    plugins: []
    include_data_dirs: []

runtime:
  database: external
  cache: external
  provider: external

security:
  compile: true
  strip_symbols: true
  sign: false
  sbom: false
  checksums: true
  signing:
    enabled: false

release:
  channel: stable
  upgrade:
    enabled: false

pack:
  output_dir: dist/pack
  targets:
    - os: windows
      arch: x64
      shell: headless
      format: dir
"""


def _seed_project(tmp_path: Path) -> Path:
    project = tmp_path / "app"
    (project / "frontend" / "dist").mkdir(parents=True)
    (project / "frontend" / "dist" / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    be = project / "backend"
    be.mkdir(parents=True)
    (be / "scripts").mkdir(parents=True)
    (be / "scripts" / "run_portable.py").write_text("print('x')\n", encoding="utf-8")
    (project / "pack.manifest.yaml").write_text(_MANIFEST_YAML.strip() + "\n", encoding="utf-8")

    # Seed _work artifacts as a prior build would
    art = project / "dist" / "pack" / "_work" / "windows-x64-headless" / "artifacts"
    fe = art / "frontend" / "dist"
    fe.mkdir(parents=True)
    (fe / "index.html").write_text("<html>ok</html>", encoding="utf-8")
    be_art = art / "backend" / "run_portable"
    be_art.mkdir(parents=True)
    (be_art / "run_portable.exe").write_bytes(b"MZ")
    (art / "backend" / "PACK_BACKEND.txt").write_text("adapter=python-nuitka\n", encoding="utf-8")
    return project


def test_assemble_only_repackages(tmp_path: Path) -> None:
    project = _seed_project(tmp_path)
    out = run_assemble_only(
        project_root=project,
        target_key="windows-x64-headless",
        skip_release=True,
    )
    assert out.is_dir()
    assert (out / "VERSION").is_file()
    assert (out / "start.bat").is_file()
    assert (out / "config-wizard.bat").is_file()
    assert (out / "service" / "asm.service").is_file()


def test_msi_emits_heat_script(tmp_path: Path) -> None:
    project = tmp_path / "app"
    fe = project / "frontend" / "dist"
    be = project / "backend"
    fe.mkdir(parents=True)
    be.mkdir(parents=True)
    (fe / "index.html").write_text("ok", encoding="utf-8")
    (be / "scripts").mkdir(parents=True)
    (be / "scripts" / "run_portable.py").write_text("x\n", encoding="utf-8")

    manifest = PackManifest(
        product=ProductSpec(name="msiapp", version="1.2.3", appId="com.msi"),
        frontend=FrontendSpec(dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(adapter="python-nuitka", dir="backend", entry="scripts/run_portable.py"),
        pack=PackSpec(
            output_dir=str(tmp_path / "out"),
            targets=[
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=ShellKind.HEADLESS,
                    format=PackageFormat.MSI,
                )
            ],
        ),
    )
    ctx = BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=manifest,
        target=manifest.pack.targets[0],
        skip_frontend=True,
        skip_backend=True,
    )
    art_fe = ctx.artifacts_dir / "frontend" / "dist"
    art_fe.mkdir(parents=True)
    (art_fe / "index.html").write_text("ok", encoding="utf-8")
    art_be = ctx.artifacts_dir / "backend" / "run_portable"
    art_be.mkdir(parents=True)
    (art_be / "run_portable.exe").write_bytes(b"MZ")

    assemble = HeadlessShellAssembler().assemble(ctx)
    final = MsiPackager().package(ctx, assemble)
    wix = ctx.output_dir / f"{ctx.artifact_name}.wix"
    assert (wix / "Product.wxs").is_file()
    ps1 = (wix / "build-msi.ps1").read_text(encoding="utf-8")
    assert "heat dir" in ps1
    assert str(final) in ps1 or "PAYLOAD" not in ps1
    assert "candle" in ps1 and "light" in ps1
