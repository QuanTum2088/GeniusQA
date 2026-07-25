#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
Minium 执行器 - 微信小程序官方自动化框架
支持：微信开发者工具模拟器 / Android / iOS 三端
pip install minium
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseMiniRunner


class MiniumRunner(BaseMiniRunner):
    """
    基于腾讯官方 minium 框架的微信小程序自动化执行器

    platform_config 字段：
      dev_tool_path  - 微信开发者工具可执行文件路径
      project_path   - 小程序项目目录
      appid          - 小程序 AppID（可选）
      platform       - ide（模拟器）| android | ios，默认 ide
    """

    FRAMEWORK_NAME = "minium"
    SUPPORTED_PLATFORMS = ["wechat"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mini = None    # minium.Minium 实例
        self._app = None     # minium.App 实例

    def _get_minium(self):
        try:
            import minium
            return minium
        except ImportError:
            raise ImportError("请安装 minium: pip install minium")

    def screenshot(self, save_path: str) -> None:
        if self._app:
            try:
                self._app.screen_shot(save_path)
                return
            except Exception:
                pass
        # 降级截图
        try:
            import pyautogui
            pyautogui.screenshot(save_path)
        except ImportError:
            pass

    def launch(self, **kwargs) -> None:
        minium = self._get_minium()
        cfg = self.platform_config

        config = minium.MiniConfig(
            dev_tool_path=cfg.get("dev_tool_path", ""),
            project_path=cfg.get("project_path", ""),
            platform=cfg.get("platform", "ide"),
        )
        self._mini = minium.Minium(config)
        self._app = self._mini.app
        time.sleep(2)

    def navigate(self, page_path: str, **kwargs) -> None:
        if not self._app:
            raise RuntimeError("小程序未启动，请先执行 launch")
        self._app.navigate_to(page_path)
        time.sleep(0.5)

    def click(self, selector: str, selector_type: str = "css", **kwargs) -> None:
        page = self._app.get_current_page()
        elem = page.get_element(selector)
        elem.click()

    def input_text(self, selector: str, value: str, selector_type: str = "css", **kwargs) -> None:
        page = self._app.get_current_page()
        elem = page.get_element(selector)
        elem.input(value)

    def get_text(self, selector: str, selector_type: str = "css") -> str:
        page = self._app.get_current_page()
        elem = page.get_element(selector)
        return elem.inner_text or ""

    def swipe(self, direction: str, distance: int, **kwargs) -> None:
        page = self._app.get_current_page()
        dir_map = {
            "up":    (0, -distance),
            "down":  (0, distance),
            "left":  (-distance, 0),
            "right": (distance, 0),
        }
        dx, dy = dir_map.get(direction, (0, distance))
        page.scroll_to(dy)

    def call_api(self, api_name: str, params: Optional[Dict] = None) -> Any:
        """调用小程序 wx.xxx API"""
        if not self._app:
            raise RuntimeError("小程序未启动")
        return self._app.call_wx_method(api_name, params or {})

    def execute_js(self, js_code: str) -> Any:
        page = self._app.get_current_page()
        return page.evaluate(js_code)

    def close(self, **kwargs) -> None:
        if self._mini:
            try:
                self._mini.shutdown()
            except Exception:
                pass
            self._mini = None
            self._app = None
