#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Portable deploy: load root config.yaml, then full DB init (cli.py init-db --yes)."""
import os
import subprocess
import sys

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_SCRIPTS_DIR)
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


def main() -> int:
    from portable_env import load_portable_yaml_into_environ

    if not load_portable_yaml_into_environ():
        print(
            "Missing config.yaml. Copy config.example.yaml to config.yaml beside start.bat "
            "and set database (and Redis) before running DB init.",
            file=sys.stderr,
        )
        return 1

    cli_py = os.path.join(_SCRIPTS_DIR, "cli.py")
    proc = subprocess.run(
        [sys.executable, cli_py, "init-db", "--yes"],
        cwd=_BACKEND_DIR,
        env=os.environ.copy(),
    )
    return int(proc.returncode or 0)


if __name__ == "__main__":
    raise SystemExit(main())
