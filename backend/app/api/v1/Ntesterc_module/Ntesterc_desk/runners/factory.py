#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
执行器工厂 - 根据 framework 名称返回对应执行器实例
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Type

from .base import BaseDesktopRunner
from .pywinauto_runner import PyWinAutoRunner
from .pyautogui_runner import PyAutoGUIRunner
from .winappdriver_runner import WinAppDriverRunner

_REGISTRY: Dict[str, Type[BaseDesktopRunner]] = {
    "pywinauto":    PyWinAutoRunner,
    "pyautogui":    PyAutoGUIRunner,
    "winappdriver": WinAppDriverRunner,
}


def get_runner(
    framework: str,
    result_id: str,
    menu_id: int,
    user_id: int,
    base_dir: Path,
    **kwargs,
) -> BaseDesktopRunner:
    """
    工厂方法：根据 framework 名称创建执行器

    Args:
        framework: 框架名称，支持 pywinauto / pyautogui / winappdriver
        result_id: 执行 ID
        menu_id:   菜单 ID
        user_id:   用户 ID
        base_dir:  截图保存目录
        **kwargs:  框架特定参数（如 backend="win32"）
    """
    cls = _REGISTRY.get(framework.lower())
    if cls is None:
        supported = list(_REGISTRY.keys())
        raise ValueError(f"不支持的框架: {framework}，可选: {supported}")
    return cls(result_id=result_id, menu_id=menu_id, user_id=user_id, base_dir=base_dir, **kwargs)


def list_frameworks() -> list:
    """返回所有已注册的框架名称"""
    return list(_REGISTRY.keys())
