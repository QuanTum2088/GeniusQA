#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
Playwright 执行器 - H5/WebView 小程序自动化
适用于：H5 小程序、内嵌 WebView 的小程序
pip install playwright && playwright install
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

from .base import BaseMiniRunner


class PlaywrightMiniRunner(BaseMiniRunner):
    """
    基于 Playwright 的 H5/WebView 小程序执行器

    platform_config 字段：
      browser    - chromium | webkit | firefox，默认 chromium
      mini_url   - H5 小程序入口 URL
      headless   - 是否无头模式，默认 False（方便调试）
    """

    FRAMEWORK_NAME = "playwright"
    SUPPORTED_PLATFORMS = ["generic", "alipay", "wechat"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._playwright = None
        self._browser = None
        self._page = None

    def _pw(self):
        try:
            from playwright.sync_api import sync_playwright
            return sync_playwright
        except ImportError:
            raise ImportError("请安装 playwright: pip install playwright && playwright install")

    def screenshot(self, save_path: str) -> None:
        if self._page:
            self._page.screenshot(path=save_path)

    def launch(self, **kwargs) -> None:
        sync_playwright = self._pw()
        cfg = self.platform_config
        browser_type = cfg.get("browser", "chromium")
        headless = cfg.get("headless", False)
        mini_url = cfg.get("mini_url", "")

        self._playwright = sync_playwright().start()
        browser_obj = getattr(self._playwright, browser_type)
        self._browser = browser_obj.launch(headless=headless)
        self._page = self._browser.new_page()

        if mini_url:
            self._page.goto(mini_url)
            self._page.wait_for_load_state("networkidle")

    def navigate(self, page_path: str, **kwargs) -> None:
        if self._page:
            self._page.goto(page_path)
            self._page.wait_for_load_state("networkidle")

    def click(self, selector: str, selector_type: str = "css", **kwargs) -> None:
        if selector_type == "xpath":
            self._page.click(f"xpath={selector}")
        else:
            self._page.click(selector)

    def input_text(self, selector: str, value: str, selector_type: str = "css", **kwargs) -> None:
        if selector_type == "xpath":
            self._page.fill(f"xpath={selector}", value)
        else:
            self._page.fill(selector, value)

    def get_text(self, selector: str, selector_type: str = "css") -> str:
        if selector_type == "xpath":
            return self._page.inner_text(f"xpath={selector}")
        return self._page.inner_text(selector)

    def swipe(self, direction: str, distance: int, **kwargs) -> None:
        """模拟滚动"""
        scroll_map = {
            "up":    (0, -distance),
            "down":  (0, distance),
            "left":  (-distance, 0),
            "right": (distance, 0),
        }
        dx, dy = scroll_map.get(direction, (0, distance))
        self._page.evaluate(f"window.scrollBy({dx}, {dy})")

    def execute_js(self, js_code: str) -> Any:
        return self._page.evaluate(js_code)

    def assert_image(self, template_path: str, threshold: float = 0.8) -> Tuple[bool, str]:
        """截图后用 OpenCV 做模板匹配"""
        import tempfile, os
        tmp = tempfile.mktemp(suffix=".png")
        self._page.screenshot(path=tmp)
        try:
            import cv2, numpy as np
            screen = cv2.imread(tmp)
            tpl = cv2.imread(template_path)
            if screen is None or tpl is None:
                return False, "截图或模板图像读取失败"
            res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val >= threshold:
                return True, f"图像匹配成功，相似度={max_val:.2f}"
            return False, f"图像匹配失败，相似度={max_val:.2f}"
        except ImportError:
            return False, "图像断言需要安装 opencv-python"
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass

    def close(self, **kwargs) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._page = self._browser = self._playwright = None
