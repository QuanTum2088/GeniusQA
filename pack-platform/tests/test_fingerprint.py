"""Tests for incremental fingerprint helpers."""

from __future__ import annotations

from pathlib import Path

from pack.util.fingerprint import (
    fingerprint_matches,
    frontend_build_fingerprint,
    hash_paths,
    write_fingerprint,
)


def test_hash_paths_stable(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.py").write_text("x=1\n", encoding="utf-8")
    d1 = hash_paths([src], extra={"k": 1})
    d2 = hash_paths([src], extra={"k": 1})
    assert d1 == d2
    (src / "a.py").write_text("x=2\n", encoding="utf-8")
    d3 = hash_paths([src], extra={"k": 1})
    assert d1 != d3


def test_fingerprint_roundtrip(tmp_path: Path) -> None:
    art = tmp_path / "artifact"
    art.mkdir()
    write_fingerprint(art, digest="abc", kind="test", meta={"n": 1})
    assert fingerprint_matches(art, "abc")
    assert not fingerprint_matches(art, "zzz")


def test_frontend_fingerprint_sees_env(tmp_path: Path) -> None:
    fe = tmp_path / "frontend"
    fe.mkdir()
    (fe / "package.json").write_text("{}", encoding="utf-8")
    src = fe / "src"
    src.mkdir()
    (src / "main.ts").write_text("console.log(1)\n", encoding="utf-8")
    a = frontend_build_fingerprint(
        fe_dir=fe, install_cmd="yarn", build_cmd="yarn build", vite_api_base_url=""
    )
    b = frontend_build_fingerprint(
        fe_dir=fe,
        install_cmd="yarn",
        build_cmd="yarn build",
        vite_api_base_url="http://example.com",
    )
    assert a != b
