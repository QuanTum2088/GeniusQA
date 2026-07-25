#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""
WinAppDriver 执行器（Appium 协议，支持 UWP/Win32）
需要本地运行 WinAppDriver.exe
"""
from __future__ import annotations

import os
import time
from typing import Any, Tuple

from .base import BaseDesktopRunner


class WinAppDriverRunner(BaseDesktopRunner):
    """
    基于 WinAppDriver（Appium）的桌面自动化执行器
    定位方式：accessibility_id | xpath | name | class_name | id
    """

    FRAMEWORK_NAME = "winappdriver"

    def __init__(self, *args, server_url: str = "http://127.0.0.1:4723", **kwargs):
        super().__init__(*args, **kwargs)
        self._server_url = server_url
        self._driver = None

    def _appium(self):
        try:
            from appium import webdriver as appium_driver
            return appium_driver
        except ImportError:
            raise ImportError("请安装 Appium Python Client: pip install Appium-Python-Client")

    def screenshot(self, save_path: str) -> None:
        if self._driver:
            self._driver.save_screenshot(save_path)
        else:
            try:
                import pyautogui
                pyautogui.screenshot(save_path)
            except ImportError:
                pass

    def start_app(self, app_path: str, **kwargs) -> None:
        appium = self._appium()
        caps = {
            "app": app_path,
            "platformName": "Windows",
            "deviceName": "WindowsPC",
        }
        self._driver = appium.Remote(
            command_executor=self._server_url,
            desired_capabilities=caps,
        )
        time.sleep(1)

    def connect_app(self, locate_by: str, locate_value: str, **kwargs) -> None:
        appium = self._appium()
        caps = {
            "app": "Root",
            "platformName": "Windows",
            "deviceName": "WindowsPC",
        }
        root_driver = appium.Remote(
            command_executor=self._server_url,
            desired_capabilities=caps,
        )
        # 通过窗口名找到进程 ID
        from appium.webdriver.common.appiumby import AppiumBy
        win = root_driver.find_element(AppiumBy.NAME, locate_value)
        pid = win.get_attribute("NativeWindowHandle")
        root_driver.quit()

        caps2 = {
            "appTopLevelWindow": hex(int(pid)),
            "platformName": "Windows",
            "deviceName": "WindowsPC",
        }
        self._driver = appium.Remote(
            command_executor=self._server_url,
            desired_capabilities=caps2,
        )

    def _find(self, locate_by: str, locate_value: str):
        from appium.webdriver.common.appiumby import AppiumBy
        by_map = {
            "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
            "xpath":            AppiumBy.XPATH,
            "name":             AppiumBy.NAME,
            "class_name":       AppiumBy.CLASS_NAME,
            "id":               AppiumBy.ID,
        }
        by = by_map.get(locate_by, AppiumBy.NAME)
        return self._driver.find_element(by, locate_value)

    def click(self, locate_by: str, locate_value: str, **kwargs) -> None:
        self._find(locate_by, locate_value).click()

    def input_text(self, locate_by: str, locate_value: str, value: str, **kwargs) -> None:
        elem = self._find(locate_by, locate_value)
        elem.clear()
        elem.send_keys(value)

    def key_press(self, value: str, **kwargs) -> None:
        from selenium.webdriver.common.keys import Keys
        key_map = {
            "enter": Keys.ENTER, "tab": Keys.TAB, "esc": Keys.ESCAPE,
            "backspace": Keys.BACK_SPACE, "delete": Keys.DELETE,
            "space": Keys.SPACE,
        }
        k = key_map.get(value.lower(), value)
        self._driver.find_element("xpath", "//*").send_keys(k)

    def close_app(self, **kwargs) -> None:
        if self._driver:
            self._driver.quit()
            self._driver = None
