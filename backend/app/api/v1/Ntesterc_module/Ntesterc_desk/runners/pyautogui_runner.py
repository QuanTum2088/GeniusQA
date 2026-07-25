#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
PyAutoGUI 执行器（跨平台图像识别方案）
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Tuple

from .base import BaseDesktopRunner


class PyAutoGUIRunner(BaseDesktopRunner):
    """
    基于 pyautogui 的桌面自动化执行器
    定位方式：image（图像匹配）| coordinate（坐标）
    """

    FRAMEWORK_NAME = "pyautogui"

    def _gui(self):
        try:
            import pyautogui
            return pyautogui
        except ImportError:
            raise ImportError("请安装 pyautogui: pip install pyautogui")

    def screenshot(self, save_path: str) -> None:
        self._gui().screenshot(save_path)

    def start_app(self, app_path: str, **kwargs) -> None:
        import subprocess
        self._proc = subprocess.Popen(app_path)
        time.sleep(2)

    def connect_app(self, locate_by: str, locate_value: str, **kwargs) -> None:
        # pyautogui 无窗口句柄概念，仅记录
        self._connected_title = locate_value

    def _locate_center(self, locate_by: str, locate_value: str):
        gui = self._gui()
        if locate_by == "image":
            pos = gui.locateCenterOnScreen(locate_value, confidence=0.8)
            if pos is None:
                raise RuntimeError(f"未找到图像: {locate_value}")
            return pos
        elif locate_by == "coordinate":
            x, y = map(int, locate_value.split(","))
            return x, y
        else:
            raise ValueError(f"pyautogui 不支持定位方式: {locate_by}，请使用 image 或 coordinate")

    def click(self, locate_by: str, locate_value: str, **kwargs) -> None:
        pos = self._locate_center(locate_by, locate_value)
        self._gui().click(pos)

    def input_text(self, locate_by: str, locate_value: str, value: str, **kwargs) -> None:
        pos = self._locate_center(locate_by, locate_value)
        self._gui().click(pos)
        self._gui().typewrite(value, interval=0.05)

    def key_press(self, value: str, **kwargs) -> None:
        keys = value.split("+")
        if len(keys) > 1:
            self._gui().hotkey(*keys)
        else:
            self._gui().press(value)

    def close_app(self, **kwargs) -> None:
        if hasattr(self, "_proc") and self._proc:
            self._proc.terminate()
            self._proc = None

    def assert_image(self, template_path: str, threshold: float = 0.8) -> Tuple[bool, str]:
        gui = self._gui()
        try:
            pos = gui.locateCenterOnScreen(template_path, confidence=threshold)
            if pos:
                return True, f"图像匹配成功: {template_path}"
            return False, f"未找到图像: {template_path}"
        except Exception as e:
            return False, str(e)
