"""Tests for bundled nginx layout."""

from __future__ import annotations

import zipfile
from pathlib import Path

from pack.context import BuildContext
from pack.models import (
    BackendSpec,
    FrontendSpec,
    NginxBundleSpec,
    PackManifest,
    PackSpec,
    PackTarget,
    PackageFormat,
    ProductSpec,
    RuntimeSpec,
    SecuritySpec,
    ShellKind,
    TargetArch,
    TargetOS,
)
from pack.pipeline.runner import platform_root
from pack.runtime.nginx_bundle import bundle_nginx


def _manifest() -> PackManifest:
    return PackManifest(
        product=ProductSpec(name="nginxapp", version="1.0.0", appId="com.nginx"),
        frontend=FrontendSpec(adapter="vite", dir="frontend", dist="frontend/dist"),
        backend=BackendSpec(adapter="python-nuitka", dir="backend", entry="scripts/run_portable.py"),
        runtime=RuntimeSpec(
            nginx=NginxBundleSpec(enabled=True, archive="nginx-test.zip", listen_port=80, backend_port=8100)
        ),
        security=SecuritySpec(compile=False, sbom=False, checksums=False),
        pack=PackSpec(
            output_dir="dist/pack",
            targets=[
                PackTarget(
                    os=TargetOS.WINDOWS,
                    arch=TargetArch.X64,
                    shell=ShellKind.HEADLESS,
                    format=PackageFormat.ZIP,
                )
            ],
        ),
    )


def _write_fake_nginx_zip(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("nginx-1.0/conf/mime.types", "types { text/html html; }\n")
        zf.writestr("nginx-1.0/conf/nginx.conf", "events {}\n")
        zf.writestr("nginx-1.0/nginx.exe", "fake")


def test_bundle_nginx_extracts_and_writes_template(tmp_path: Path) -> None:
    project = tmp_path / "app"
    project.mkdir()
    archive = project / "nginx-test.zip"
    _write_fake_nginx_zip(archive)
    manifest = _manifest()
    ctx = BuildContext.create(
        project_root=project,
        platform_root=platform_root(),
        manifest=manifest,
        target=manifest.pack.targets[0],
        skip_frontend=True,
        skip_backend=True,
    )
    assemble = tmp_path / "assemble"
    assemble.mkdir()
    (assemble / "app" / "frontend").mkdir(parents=True)
    (assemble / "app" / "frontend" / "index.html").write_text("ok", encoding="utf-8")

    dest = bundle_nginx(ctx, assemble)
    assert (dest / "nginx.exe").is_file()
    assert (dest / "conf" / "ntester.conf.template").is_file()
    text = (dest / "conf" / "ntester.conf.template").read_text(encoding="utf-8")
    assert "listen       80;" in text
    assert "{INSTALL_ROOT}/app/frontend" in text
    assert "Ntesterc_ai/conversation" in text
    assert 'proxy_set_header Upgrade $http_upgrade;' in text
    assert 'Connection "upgrade"' in text
