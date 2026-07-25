#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
Appium 执行器 - 通用小程序自动化（支付宝/抖音/百度/微信 Android）
通过 Appium + uiautomator2/XCUITest 驱动宿主 App 内的小程序
pip install Appium-Python-Client
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseMiniRunner

# 各平台宿主 App 默认包名
PLATFORM_PACKAGES = {
    "wechat":  {"package": "com.tencent.mm",    "activity": ".ui.LauncherUI"},
    "alipay":  {"package": "com.eg.android.AlipayGphone", "activity": ".AlipayLogin"},
    "douyin":  {"package": "com.ss.android.ugc.aweme",    "activity": ".main.MainActivity"},
    "baidu":   {"package": "com.baidu.searchbox",         "activity": ".MainActivity"},
}


class AppiumMiniRunner(BaseMiniRunner):
    """
    基于 Appium 的通用小程序执行器
    适用于：支付宝、抖音、百度、微信（Android/iOS）

    platform_config 字段：
      appium_server  - Appium 服务地址，默认 http://127.0.0.1:4723
      device_id      - 设备 ID（adb devices 中的序列号）
      platform_name  - Android | iOS
      app_package    - 宿主 App 包名（不填则按 platform 自动推断）
      app_activity   - 宿主 App Activity
      platform       - wechat | alipay | douyin | baidu | generic
    """

    FRAMEWORK_NAME = "appium"
    SUPPORTED_PLATFORMS = ["wechat", "alipay", "douyin", "baidu", "generic"]

    def __init__(self, *args, platform: str = "generic", **kwargs):
        super().__init__(*args, **kwargs)
        self._platform = platform
        self._driver = None

    def _appium(self):
        try:
            from appium import webdriver
            return webdriver
        except ImportError:
            raise ImportError("请安装 Appium Python Client: pip install Appium-Python-Client")

    def screenshot(self, save_path: str) -> None:
        if self._driver:
            self._driver.save_screenshot(save_path)

    def launch(self, **kwargs) -> None:
        webdriver = self._appium()
        cfg = self.platform_config
        server = cfg.get("appium_server", "http://127.0.0.1:4723")
        platform_name = cfg.get("platform_name", "Android")

        # 自动推断包名
        pkg_info = PLATFORM_PACKAGES.get(self._platform, {})
        app_package = cfg.get("app_package") or pkg_info.get("package", "")
        app_activity = cfg.get("app_activity") or pkg_info.get("activity", "")

        # Appium 2.x / Python Client 4.x 使用 Options 对象，不再支持 desired_capabilities
        if platform_name == "Android":
            try:
                from appium.options.android import UiAutomator2Options
                opts = UiAutomator2Options()
            except ImportError:
                from appium.webdriver.appium_service import AppiumService
                opts = webdriver.AppiumOptions()
            opts.platform_name = "Android"
            opts.device_name = cfg.get("device_id", "")
            if cfg.get("device_id"):
                opts.udid = cfg["device_id"]
            opts.app_package = app_package
            opts.app_activity = app_activity
            opts.no_reset = True
            opts.new_command_timeout = 3600
        else:
            try:
                from appium.options.ios import XCUITestOptions
                opts = XCUITestOptions()
            except ImportError:
                opts = webdriver.AppiumOptions()
            opts.platform_name = "iOS"
            opts.device_name = cfg.get("device_id", "")
            if cfg.get("device_id"):
                opts.udid = cfg["device_id"]
            opts.no_reset = True
            opts.new_command_timeout = 3600

        self._driver = webdriver.Remote(
            command_executor=server,
            options=opts,
        )
        time.sleep(3)

    def navigate(self, page_path: str, **kwargs) -> None:
        """
        通用导航：通过 deep link 或 URL scheme 跳转小程序页面
        微信：weixin://dl/business/?t=xxx
        支付宝：alipays://platformapi/startapp?appId=xxx&page=xxx
        """
        if not page_path:
            return
        scheme_map = {
            "wechat": f"weixin://dl/business/?t={page_path}",
            "alipay": f"alipays://platformapi/startapp?page={page_path}",
        }
        scheme = scheme_map.get(self._platform, page_path)
        try:
            self._driver.execute_script("mobile: deepLink", {"url": scheme, "package": ""})
        except Exception:
            # 降级：直接 adb am start
            pass
        time.sleep(1)

    def _find(self, selector: str, selector_type: str = "css"):
        from appium.webdriver.common.appiumby import AppiumBy
        by_map = {
            "css":              AppiumBy.ANDROID_UIAUTOMATOR,
            "xpath":            AppiumBy.XPATH,
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "id":               AppiumBy.ID,
            "class_name":       AppiumBy.CLASS_NAME,
        }
        by = by_map.get(selector_type, AppiumBy.XPATH)
        if selector_type == "css":
            # 将 CSS 选择器转为 UiSelector（简单映射）
            ui_selector = f'new UiSelector().resourceId("{selector}")'
            return self._driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, ui_selector)
        return self._driver.find_element(by, selector)

    def click(self, selector: str, selector_type: str = "css", **kwargs) -> None:
        self._find(selector, selector_type).click()

    def input_text(self, selector: str, value: str, selector_type: str = "css", **kwargs) -> None:
        elem = self._find(selector, selector_type)
        elem.clear()
        elem.send_keys(value)

    def get_text(self, selector: str, selector_type: str = "css") -> str:
        return self._find(selector, selector_type).text or ""

    def swipe(self, direction: str, distance: int, **kwargs) -> None:
        size = self._driver.get_window_size()
        w, h = size["width"], size["height"]
        cx, cy = w // 2, h // 2
        dir_map = {
            "up":    (cx, cy + distance // 2, cx, cy - distance // 2),
            "down":  (cx, cy - distance // 2, cx, cy + distance // 2),
            "left":  (cx + distance // 2, cy, cx - distance // 2, cy),
            "right": (cx - distance // 2, cy, cx + distance // 2, cy),
        }
        x1, y1, x2, y2 = dir_map.get(direction, (cx, cy, cx, cy + distance))
        self._driver.swipe(x1, y1, x2, y2, duration=500)

    def execute_js(self, js_code: str) -> Any:
        return self._driver.execute_script(js_code)

    def close(self, **kwargs) -> None:
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
