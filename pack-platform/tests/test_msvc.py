"""Tests for MSVC discovery helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pack.util.msvc import (
    MsvcInfo,
    find_cl_under_vs,
    install_hint,
    probe_msvc,
    winget_install_command,
)


def test_winget_command_shape() -> None:
    cmd = winget_install_command()
    assert cmd[0] == "winget"
    assert "Microsoft.VisualStudio.2022.BuildTools" in cmd
    assert "--override" in cmd


def test_install_hint_mentions_setup() -> None:
    text = install_hint()
    assert "setup-msvc" in text
    assert "Build Tools" in text


def test_find_cl_under_vs_layout(tmp_path: Path) -> None:
    root = tmp_path / "VS"
    cl = (
        root
        / "VC"
        / "Tools"
        / "MSVC"
        / "14.40.33807"
        / "bin"
        / "Hostx64"
        / "x64"
        / "cl.exe"
    )
    cl.parent.mkdir(parents=True)
    cl.write_bytes(b"MZ")
    found = find_cl_under_vs(root)
    assert found == cl


def test_probe_msvc_prefers_path(tmp_path: Path) -> None:
    fake_cl = tmp_path / "cl.exe"
    fake_cl.write_bytes(b"MZ")
    with (
        patch("pack.util.msvc.os.name", "nt"),
        patch("pack.util.msvc.which", return_value=str(fake_cl)),
        patch("pack.util.msvc.find_vs_install", return_value=None),
        patch("pack.util.msvc.find_vcvarsall", return_value=None),
    ):
        info = probe_msvc()
    assert isinstance(info, MsvcInfo)
    assert info.on_path is True
    assert info.cl == fake_cl
