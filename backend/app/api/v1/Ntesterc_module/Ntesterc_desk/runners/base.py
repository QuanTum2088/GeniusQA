#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
客户端UI自动化 - 执行器基类所有框架执行器继承此类，实现统一接口
"""
from __future__ import annotations

import abc
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class StepResult:
    """单步执行结果"""
    def __init__(
        self,
        name: str,
        status: int,          # 0=失败 1=成功
        log: str = "",
        before_img: str = "",
        after_img: str = "",
        assert_value: Optional[Dict] = None,
    ):
        self.name = name
        self.status = status
        self.log = log
        self.before_img = before_img
        self.after_img = after_img
        self.assert_value = assert_value or {}


class BaseDesktopRunner(abc.ABC):
    """
    桌面自动化执行器基类
    子类需实现：
      - start_app / connect_app / close_app
      - click / input_text / key_press
      - screenshot
      - assert_image（可选）
    """

    FRAMEWORK_NAME: str = "base"

    def __init__(self, result_id: str, menu_id: int, user_id: int, base_dir: Path):
        self.result_id = result_id
        self.menu_id = menu_id
        self.user_id = user_id
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._app = None          # 当前应用句柄
        self._window = None       # 当前窗口句柄
        self._step_idx = 0

    # ── 截图 ──────────────────────────────────────────────
    def _save_screenshot(self, tag: str) -> str:
        """截图并保存，返回相对 URL"""
        ts = int(time.time() * 1000)
        fname = f"{tag}_{self._step_idx}_{ts}.png"
        fpath = self.base_dir / fname
        try:
            self.screenshot(str(fpath))
            return f"/static/desktop_result/{self.result_id}/{fname}"
        except Exception:
            return ""

    # ── 抽象接口 ──────────────────────────────────────────
    @abc.abstractmethod
    def screenshot(self, save_path: str) -> None:
        """截图保存到 save_path"""

    @abc.abstractmethod
    def start_app(self, app_path: str, **kwargs) -> None:
        """启动应用"""

    @abc.abstractmethod
    def connect_app(self, locate_by: str, locate_value: str, **kwargs) -> None:
        """连接已有窗口"""

    @abc.abstractmethod
    def click(self, locate_by: str, locate_value: str, **kwargs) -> None:
        """点击元素"""

    @abc.abstractmethod
    def input_text(self, locate_by: str, locate_value: str, value: str, **kwargs) -> None:
        """输入文本"""

    @abc.abstractmethod
    def key_press(self, value: str, **kwargs) -> None:
        """按键"""

    @abc.abstractmethod
    def close_app(self, **kwargs) -> None:
        """关闭应用"""

    def assert_image(self, template_path: str, threshold: float = 0.8) -> Tuple[bool, str]:
        """图像断言（可选实现）"""
        return False, "当前框架不支持图像断言"

    def custom_command(self, command: str, **kwargs) -> None:
        """执行自定义命令（可选实现）"""
        raise NotImplementedError(f"{self.FRAMEWORK_NAME} 不支持自定义命令")

    # 需要截图的步骤类型（有界面交互的步骤）
    _SCREENSHOT_TYPES = {0, 1, 2, 3, 5, 7, 8}

    # ── 步骤分发 ──────────────────────────────────────────
    def execute_step(self, step: Dict[str, Any]) -> StepResult:
        """执行单个步骤，返回 StepResult"""
        self._step_idx += 1
        name = step.get("name") or f"步骤{self._step_idx}"
        step_type = int(step.get("type", -1))
        wait = float(step.get("wait") or 0)

        # 只对有界面交互的步骤截图，减少 I/O 压力
        need_screenshot = step_type in self._SCREENSHOT_TYPES
        before_img = self._save_screenshot("before") if need_screenshot else ""

        ok = True
        log_msg = "执行成功"
        assert_value: Dict = {}

        try:
            if step_type == 0:          # 启动应用
                self.start_app(step.get("app_path", ""))
            elif step_type == 1:        # 连接已有窗口
                self.connect_app(
                    step.get("locate_by", "title"),
                    step.get("locate_value", ""),
                )
            elif step_type == 2:        # 点击
                self.click(
                    step.get("locate_by", "title"),
                    step.get("locate_value", ""),
                )
            elif step_type == 3:        # 输入文本
                self.input_text(
                    step.get("locate_by", "title"),
                    step.get("locate_value", ""),
                    step.get("value", ""),
                )
            elif step_type == 4:        # 按键
                self.key_press(step.get("value", ""))
            elif step_type == 5:        # 截图断言
                passed, msg = self.assert_image(step.get("assert_img", ""))
                assert_value = {"passed": passed, "message": msg}
                if not passed:
                    raise AssertionError(msg)
            elif step_type == 6:        # 等待
                time.sleep(float(step.get("value") or wait or 1))
            elif step_type == 7:        # 关闭应用
                self.close_app()
            elif step_type == 8:        # 自定义命令
                self.custom_command(step.get("command", ""))
            else:
                log_msg = f"未知步骤类型: {step_type}"

            if wait > 0 and step_type != 6:
                time.sleep(wait)

        except Exception as e:
            ok = False
            log_msg = str(e)

        after_img = self._save_screenshot("after") if need_screenshot else ""

        return StepResult(
            name=name,
            status=1 if ok else 0,
            log=log_msg,
            before_img=before_img,
            after_img=after_img,
            assert_value=assert_value,
        )

    def run_steps(self, steps: List[Dict[str, Any]]) -> List[StepResult]:
        """执行所有步骤"""
        results = []
        for step in steps:
            results.append(self.execute_step(step))
        return results
