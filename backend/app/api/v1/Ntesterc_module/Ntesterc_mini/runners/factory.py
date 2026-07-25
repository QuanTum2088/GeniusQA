#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
小程序执行器工厂
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Type

from .base import BaseMiniRunner
from .minium_runner import MiniumRunner
from .appium_runner import AppiumMiniRunner
from .playwright_runner import PlaywrightMiniRunner

# framework -> class
_REGISTRY: Dict[str, Type[BaseMiniRunner]] = {
    "minium":     MiniumRunner,
    "appium":     AppiumMiniRunner,
    "playwright": PlaywrightMiniRunner,
}

# platform -> 推荐框架列表
PLATFORM_FRAMEWORKS: Dict[str, list] = {
    "wechat":  ["minium", "appium"],
    "alipay":  ["appium", "playwright"],
    "douyin":  ["appium"],
    "baidu":   ["appium"],
    "generic": ["appium", "playwright"],
}


def get_runner(
    framework: str,
    platform: str,
    result_id: str,
    menu_id: int,
    user_id: int,
    base_dir: Path,
    platform_config: Dict[str, Any],
) -> BaseMiniRunner:
    cls = _REGISTRY.get(framework.lower())
    if cls is None:
        raise ValueError(f"不支持的框架: {framework}，可选: {list(_REGISTRY.keys())}")

    kwargs: Dict[str, Any] = {}
    if framework == "appium":
        kwargs["platform"] = platform

    return cls(
        result_id=result_id,
        menu_id=menu_id,
        user_id=user_id,
        base_dir=base_dir,
        platform_config=platform_config,
        **kwargs,
    )


def list_frameworks() -> list:
    return list(_REGISTRY.keys())


def list_platforms() -> Dict[str, list]:
    return PLATFORM_FRAMEWORKS
