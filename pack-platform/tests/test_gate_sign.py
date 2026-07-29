"""Production gate and signing pending tests."""

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
    ShellKind,
    TargetArch,
    TargetOS,
)
from pack.pipeline.preflight import ProductionGateError, run_preflight
from pack.pipeline.runner import platform_root
from pack.security.signing import sign_artifact


def _ctx(tmp_path: Path, *, shell: ShellKind, fmt: PackageFormat) -> BuildContext:
    project = tmp_path / "proj"
    (project / "frontend").mkdir(parents=True)
    (project / "backend").mkdir(parents=True)
    (project / "backend" / "main.py").write_text("print(1)\n", encoding="utf-8")
    man = PackManifest(
        product=ProductSpec(name="g", version="1.0.0", appId="com.g"),
        frontend=FrontendSpec(dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(adapter="python-nuitka", dir="backend", entry="main.py"),
        pack=PackSpec(
            output_dir=str(tmp_path / "dist"),
            targets=[
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=shell,
                    format=fmt,
                )
            ],
        ),
    )
    return BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=man,
        target=man.pack.targets[0],
    )


def test_production_gate_blocks_tauri(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path, shell=ShellKind.TAURI, fmt=PackageFormat.DIR)
    with pytest.raises(ProductionGateError):
        run_preflight(ctx, allow_experimental=False, skip_compiler_check=True)


def test_production_gate_allows_headless_zip_with_skip_compiler(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path, shell=ShellKind.HEADLESS, fmt=PackageFormat.ZIP)
    run_preflight(ctx, allow_experimental=False, skip_compiler_check=True)


def test_sign_pending_without_cert(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PACK_WIN_CERT_PATH", raising=False)
    ctx = _ctx(tmp_path, shell=ShellKind.HEADLESS, fmt=PackageFormat.ZIP)
    artifact = tmp_path / "app.exe"
    artifact.write_bytes(b"MZ")
    result = sign_artifact(ctx, artifact)
    assert result["status"] in {"pending", "skipped"}
    pending = ctx.output_dir / f"{ctx.artifact_name}.sign-pending.json"
    assert pending.is_file() or result["status"] == "skipped"
