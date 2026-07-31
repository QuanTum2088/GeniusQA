#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""启动入口：先加载 config.yaml，再按其中 server 段启动 uvicorn。"""
import os
import sys

# 确保可导入同目录下的 main、portable_env
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

if __name__ == "__main__":
    import traceback
    from pathlib import Path

    from portable_env import _find_config_yaml, load_portable_yaml_into_environ

    cfg = _find_config_yaml()
    if cfg:
        os.chdir(cfg.parent)
    portable_root = Path(os.environ.get("NT_PORTABLE_ROOT") or os.getcwd())
    log_dir = portable_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    startup_log = log_dir / "startup.log"

    try:
        if not load_portable_yaml_into_environ():
            raise SystemExit("config.yaml not found; run config-wizard.bat first")
        host = os.environ.get("UVICORN_HOST", "0.0.0.0")
        port = int(os.environ.get("UVICORN_PORT", "8100"))
        # Import the ASGI app directly so Nuitka follows main/config at compile time.
        # String form "main:app" is a runtime import and was missing from the standalone build.
        from main import app
        import uvicorn

        uvicorn.run(app, host=host, port=port, reload=False)
    except Exception:
        # start-backend.bat already redirects stdout/stderr to startup.log; opening the
        # same file again can raise PermissionError on Windows — never mask the real error.
        try:
            with open(startup_log, "a", encoding="utf-8") as f:
                f.write(traceback.format_exc())
                f.write("\n")
        except OSError:
            sys.stderr.write(traceback.format_exc())
            sys.stderr.write("\n")
        raise