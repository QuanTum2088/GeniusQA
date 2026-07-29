"""Host OS matching tests."""

from __future__ import annotations

import pytest

from pack.models import PackTarget, PackageFormat, ShellKind, TargetArch, TargetOS
from pack.util.host import HostMismatchError, assert_native_target, host_os, matrix_hint


def test_assert_native_ok_for_host() -> None:
    hos = host_os()
    t = PackTarget(
        os=hos,
        arch=TargetArch.X64 if hos != TargetOS.MACOS else TargetArch.ARM64,
        shell=ShellKind.HEADLESS,
        format=PackageFormat.ZIP,
    )
    # On Windows CI/dev we use x64; on Apple Silicon arm64 — skip if arch differs
    from pack.util.host import host_arch

    t = PackTarget(
        os=hos,
        arch=host_arch(),
        shell=ShellKind.HEADLESS,
        format=PackageFormat.ZIP,
    )
    assert_native_target(t)


def test_assert_mismatch_raises() -> None:
    hos = host_os()
    other = TargetOS.LINUX if hos != TargetOS.LINUX else TargetOS.WINDOWS
    t = PackTarget(
        os=other,
        arch=TargetArch.X64,
        shell=ShellKind.HEADLESS,
        format=PackageFormat.ZIP,
    )
    with pytest.raises(HostMismatchError):
        assert_native_target(t)


def test_matrix_hint_lists_headless() -> None:
    targets = [
        PackTarget(
            os=TargetOS.WINDOWS,
            arch=TargetArch.X64,
            shell=ShellKind.HEADLESS,
            format=PackageFormat.ZIP,
        ),
        PackTarget(
            os=TargetOS.LINUX,
            arch=TargetArch.X64,
            shell=ShellKind.HEADLESS,
            format=PackageFormat.ZIP,
        ),
    ]
    rows = matrix_hint(targets)
    assert {r["target"] for r in rows} == {
        "windows-x64-headless",
        "linux-x64-headless",
    }
