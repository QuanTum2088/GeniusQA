#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
PyWinAuto 执行器（默认框架）
支持 Win32 和 UIA 两种后端
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Tuple

from .base import BaseDesktopRunner


class PyWinAutoRunner(BaseDesktopRunner):
    """
    基于 pywinauto 的桌面自动化执行器
    定位方式：title | class_name | auto_id | best_match
    """

    FRAMEWORK_NAME = "pywinauto"

    def __init__(self, *args, backend: str = "uia", **kwargs):
        super().__init__(*args, **kwargs)
        self._backend = backend   # "uia" 或 "win32"

    def _get_app(self):
        try:
            from pywinauto import Application
        except ImportError:
            raise ImportError("请安装 pywinauto: pip install pywinauto")
        return Application

    def screenshot(self, save_path: str) -> None:
        try:
            import pyautogui
            pyautogui.screenshot(save_path)
        except ImportError:
            # 降级：用 PIL
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img.save(save_path)
            except Exception:
                pass

    def start_app(self, app_path: str, **kwargs) -> None:
        Application = self._get_app()
        self._app = Application(backend=self._backend).start(app_path)
        import time; time.sleep(1)
        # 取最顶层窗口
        self._window = self._app.top_window()

    def connect_app(self, locate_by: str, locate_value: str, **kwargs) -> None:
        Application = self._get_app()
        connect_kwargs: dict = {}
        if locate_by == "title":
            connect_kwargs["title"] = locate_value
        elif locate_by == "class_name":
            connect_kwargs["class_name"] = locate_value
        elif locate_by == "title_re":
            connect_kwargs["title_re"] = locate_value
        else:
            connect_kwargs["title"] = locate_value

        self._app = Application(backend=self._backend).connect(**connect_kwargs)
        self._window = self._app.top_window()

    def _find_element(self, locate_by: str, locate_value: str):
        """根据定位方式查找控件"""
        if self._window is None:
            raise RuntimeError("未连接到任何窗口，请先执行 start_app 或 connect_app")

        if locate_by == "auto_id":
            return self._window.child_window(auto_id=locate_value)
        elif locate_by == "class_name":
            return self._window.child_window(class_name=locate_value)
        elif locate_by == "title":
            return self._window.child_window(title=locate_value)
        elif locate_by == "best_match":
            return self._window[locate_value]
        elif locate_by == "xpath":
            # pywinauto 不原生支持 xpath，尝试 best_match 降级
            return self._window.child_window(best_match=locate_value)
        else:
            return self._window.child_window(title=locate_value)

    def click(self, locate_by: str, locate_value: str, **kwargs) -> None:
        elem = self._find_element(locate_by, locate_value)
        elem.click_input()

    def input_text(self, locate_by: str, locate_value: str, value: str, **kwargs) -> None:
        elem = self._find_element(locate_by, locate_value)
        elem.set_focus()
        elem.type_keys(value, with_spaces=True)

    def key_press(self, value: str, **kwargs) -> None:
        if self._window:
            self._window.type_keys(value)
        else:
            try:
                import pyautogui
                pyautogui.hotkey(*value.split("+"))
            except ImportError:
                raise RuntimeError("未连接窗口且未安装 pyautogui，无法执行按键")

    def close_app(self, **kwargs) -> None:
        if self._app:
            try:
                self._app.kill()
            except Exception:
                pass
            self._app = None
            self._window = None

    def assert_image(self, template_path: str, threshold: float = 0.8) -> Tuple[bool, str]:
        """使用 OpenCV 模板匹配做图像断言"""
        if not template_path or not os.path.exists(template_path):
            return False, f"模板图像不存在: {template_path}"
        try:
            import cv2
            import numpy as np
            import pyautogui
            screen = pyautogui.screenshot()
            screen_np = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            tpl = cv2.imread(template_path)
            res = cv2.matchTemplate(screen_np, tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val >= threshold:
                return True, f"图像匹配成功，相似度={max_val:.2f}"
            return False, f"图像匹配失败，相似度={max_val:.2f} < {threshold}"
        except ImportError:
            return False, "图像断言需要安装 opencv-python 和 pyautogui"

    def custom_command(self, command: str, **kwargs) -> None:
        """自定义命令 - 生产环境已禁用，防止任意代码执行"""
        raise PermissionError("自定义命令在生产环境中已禁用，请使用标准步骤类型")
