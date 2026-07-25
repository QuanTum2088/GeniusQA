#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
小程序自动化 - 执行器基类
"""
from __future__ import annotations

import abc
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MiniStepResult:
    def __init__(self, name: str, status: int, log: str = "",
                 before_img: str = "", after_img: str = "",
                 assert_value: Optional[Dict] = None):
        self.name = name
        self.status = status
        self.log = log
        self.before_img = before_img
        self.after_img = after_img
        self.assert_value = assert_value or {}


class BaseMiniRunner(abc.ABC):
    """
    小程序自动化执行器基类
    各平台/框架子类实现具体操作
    """

    FRAMEWORK_NAME: str = "base"
    SUPPORTED_PLATFORMS: List[str] = []

    def __init__(self, result_id: str, menu_id: int, user_id: int,
                 base_dir: Path, platform_config: Dict[str, Any]):
        self.result_id = result_id
        self.menu_id = menu_id
        self.user_id = user_id
        self.base_dir = base_dir
        self.platform_config = platform_config or {}
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._step_idx = 0

    def _save_screenshot(self, tag: str) -> str:
        ts = int(time.time() * 1000)
        fname = f"{tag}_{self._step_idx}_{ts}.png"
        fpath = self.base_dir / fname
        try:
            self.screenshot(str(fpath))
            return f"/static/mini_result/{self.result_id}/{fname}"
        except Exception:
            return ""

    # ── 抽象接口 ──────────────────────────────────────────
    @abc.abstractmethod
    def screenshot(self, save_path: str) -> None: ...

    @abc.abstractmethod
    def launch(self, **kwargs) -> None:
        """启动/连接小程序"""

    @abc.abstractmethod
    def navigate(self, page_path: str, **kwargs) -> None:
        """导航到页面"""

    @abc.abstractmethod
    def click(self, selector: str, selector_type: str = "css", **kwargs) -> None: ...

    @abc.abstractmethod
    def input_text(self, selector: str, value: str, selector_type: str = "css", **kwargs) -> None: ...

    @abc.abstractmethod
    def get_text(self, selector: str, selector_type: str = "css") -> str: ...

    @abc.abstractmethod
    def swipe(self, direction: str, distance: int, **kwargs) -> None: ...

    @abc.abstractmethod
    def close(self, **kwargs) -> None:
        """关闭小程序"""

    def call_api(self, api_name: str, params: Optional[Dict] = None) -> Any:
        raise NotImplementedError(f"{self.FRAMEWORK_NAME} 不支持 call_api")

    def execute_js(self, js_code: str) -> Any:
        raise NotImplementedError(f"{self.FRAMEWORK_NAME} 不支持 execute_js")

    def assert_image(self, template_path: str, threshold: float = 0.8) -> Tuple[bool, str]:
        return False, f"{self.FRAMEWORK_NAME} 不支持图像断言"

    # 需要截图的步骤类型
    _SCREENSHOT_TYPES = {0, 1, 2, 3, 4, 5, 7, 8, 9, 10}

    # ── 步骤分发 ──────────────────────────────────────────
    def execute_step(self, step: Dict[str, Any]) -> MiniStepResult:
        self._step_idx += 1
        name = step.get("name") or f"步骤{self._step_idx}"
        step_type = int(step.get("type", -1))
        wait = float(step.get("wait") or 0)

        need_screenshot = step_type in self._SCREENSHOT_TYPES
        before_img = self._save_screenshot("before") if need_screenshot else ""
        ok = True
        log_msg = "执行成功"
        assert_value: Dict = {}

        try:
            if step_type == 0:      # 启动
                self.launch()
            elif step_type == 1:    # 导航
                self.navigate(step.get("page_path", ""))
            elif step_type == 2:    # 点击
                self.click(step.get("selector", ""), step.get("selector_type", "css"))
            elif step_type == 3:    # 输入
                self.input_text(step.get("selector", ""), step.get("value", ""),
                                 step.get("selector_type", "css"))
            elif step_type == 4:    # 获取文本断言
                text = self.get_text(step.get("selector", ""), step.get("selector_type", "css"))
                expected = step.get("assert_text", "")
                passed = expected in text if expected else True
                assert_value = {"text": text, "expected": expected, "passed": passed}
                if not passed:
                    raise AssertionError(f"文本断言失败: 期望包含 '{expected}'，实际 '{text}'")
            elif step_type == 5:    # 图像断言
                passed, msg = self.assert_image(step.get("assert_img", ""))
                assert_value = {"passed": passed, "message": msg}
                if not passed:
                    raise AssertionError(msg)
            elif step_type == 6:    # 等待
                time.sleep(float(step.get("value") or wait or 1))
            elif step_type == 7:    # 调用 API
                result = self.call_api(step.get("api_name", ""), step.get("api_params"))
                assert_value = {"result": str(result)}
            elif step_type == 8:    # 执行 JS
                result = self.execute_js(step.get("js_code", ""))
                assert_value = {"result": str(result)}
            elif step_type == 9:    # 滑动
                self.swipe(step.get("direction", "down"), int(step.get("distance") or 300))
            elif step_type == 10:   # 关闭
                self.close()
            else:
                log_msg = f"未知步骤类型: {step_type}"

            if wait > 0 and step_type not in (6,):
                time.sleep(wait)

        except Exception as e:
            ok = False
            log_msg = str(e)

        after_img = self._save_screenshot("after") if need_screenshot else ""
        return MiniStepResult(
            name=name, status=1 if ok else 0, log=log_msg,
            before_img=before_img, after_img=after_img, assert_value=assert_value,
        )

    def run_steps(self, steps: List[Dict[str, Any]]) -> List[MiniStepResult]:
        return [self.execute_step(s) for s in steps]
