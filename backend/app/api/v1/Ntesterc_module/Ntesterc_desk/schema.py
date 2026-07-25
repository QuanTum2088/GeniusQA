#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── 框架枚举 ──────────────────────────────────────────────
SUPPORTED_FRAMEWORKS = ["pywinauto", "pyautogui", "winappdriver", "sikuli"]


# ── 菜单 ──────────────────────────────────────────────────
class MenuAddBody(BaseModel):
    name: str
    pid: int = 0
    type: int = Field(0, description="0=目录 1=脚本组 2=脚本")
    project_id: Optional[int] = Field(None, description="所属项目ID")


class MenuRenameBody(BaseModel):
    id: int
    name: str


class MenuDeleteBody(BaseModel):
    id: int


# ── 脚本 ──────────────────────────────────────────────────
class ScriptSaveBody(BaseModel):
    id: int = Field(..., description="menu_id")
    framework: str = Field("pywinauto", description="执行框架")
    script: List[Dict[str, Any]] = Field(default_factory=list)


class ScriptStep(BaseModel):
    """单个脚本步骤"""
    name: str = ""
    type: int = Field(
        ...,
        description=(
            "0=启动应用 1=连接已有窗口 2=点击元素 3=输入文本 "
            "4=按键 5=截图断言 6=等待 7=关闭应用 8=自定义命令"
        )
    )
    # 定位
    locate_by: Optional[str] = Field(None, description="title|class_name|auto_id|xpath|image")
    locate_value: Optional[str] = None
    # 操作值
    value: Optional[str] = None
    # 应用路径（type=0）
    app_path: Optional[str] = None
    # 等待时间（秒）
    wait: Optional[float] = 1.0
    # 断言图像路径（type=5）
    assert_img: Optional[str] = None
    # 自定义命令（type=8，仅 pywinauto/pyautogui 支持）
    command: Optional[str] = None


# ── 执行 ──────────────────────────────────────────────────
class RunScriptBody(BaseModel):
    id: int = Field(..., description="menu_id")
    task_name: str = ""
    result_id: Optional[str] = None
    framework: str = "pywinauto"
    project_id: Optional[int] = Field(None, description="所属项目ID")


class StopScriptBody(BaseModel):
    result_id: str


class ResultListBody(BaseModel):
    page: int = 1
    pageSize: int = 10
    search: Dict[str, Any] = Field(default_factory=dict)
