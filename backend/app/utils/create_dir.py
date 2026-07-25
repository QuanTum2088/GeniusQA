# -*- coding: utf-8 -*-
# @author: rebort

from pathlib import Path


def create_dir(dir_name: str) -> Path:
    """
    在 backend 根目录下创建文件夹（相对路径时），绝对路径则原样创建。
    用于 logs 等运行时目录，不依赖进程 cwd。
    """
    path = Path(dir_name)
    if not path.is_absolute():
        # app/utils/create_dir.py -> backend
        backend_root = Path(__file__).resolve().parents[2]
        path = backend_root / dir_name
    path.mkdir(parents=True, exist_ok=True)
    return path
