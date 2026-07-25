#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# 支持的平台
SUPPORTED_PLATFORMS = ["wechat", "alipay", "douyin", "baidu", "generic"]

# 各平台推荐框架
PLATFORM_FRAMEWORKS = {
    "wechat":  ["minium", "appium"],          # 微信：官方 minium 优先
    "alipay":  ["appium", "playwright"],       # 支付宝：Appium + uiautomator2
    "douyin":  ["appium"],                     # 抖音：Appium
    "baidu":   ["appium"],                     # 百度：Appium
    "generic": ["appium", "playwright"],       # 通用：Appium / Playwright
}


class MenuAddBody(BaseModel):
    name: str
    pid: int = 0
    type: int = 0
    project_id: Optional[int] = Field(None, description="所属项目ID")


class MenuRenameBody(BaseModel):
    id: int
    name: str


class MenuDeleteBody(BaseModel):
    id: int


class PlatformConfig(BaseModel):
    """平台配置"""
    # 微信 minium 配置
    dev_tool_path: Optional[str] = Field(None, description="微信开发者工具路径")
    project_path: Optional[str] = Field(None, description="小程序项目路径")
    appid: Optional[str] = None
    # Appium 通用配置
    appium_server: Optional[str] = Field("http://127.0.0.1:4723", description="Appium 服务地址")
    device_id: Optional[str] = None
    platform_name: Optional[str] = Field("Android", description="Android | iOS")
    app_package: Optional[str] = Field(None, description="宿主 App 包名，如 com.tencent.mm")
    app_activity: Optional[str] = None
    # Playwright 配置
    browser: Optional[str] = Field("chromium", description="chromium | webkit | firefox")
    mini_url: Optional[str] = Field(None, description="H5小程序入口 URL")


class ScriptSaveBody(BaseModel):
    id: int
    platform: str = "wechat"
    framework: str = "minium"
    script: List[Dict[str, Any]] = Field(default_factory=list)
    platform_config: Optional[Dict[str, Any]] = None


class MiniStep(BaseModel):
    """
    通用步骤定义（跨平台）
    type:
      0 = 启动/连接小程序
      1 = 导航到页面
      2 = 点击元素
      3 = 输入文本
      4 = 获取元素文本（断言）
      5 = 截图断言
      6 = 等待
      7 = 调用小程序 API（minium 专属）
      8 = 执行 JS（Playwright/minium）
      9 = 滑动
      10 = 关闭小程序
    """
    name: str = ""
    type: int
    selector: Optional[str] = Field(None, description="CSS选择器 / XPath / accessibility_id")
    selector_type: Optional[str] = Field("css", description="css | xpath | accessibility_id | id")
    value: Optional[str] = None
    page_path: Optional[str] = Field(None, description="小程序页面路径，如 /pages/index/index")
    api_name: Optional[str] = Field(None, description="小程序 API 名称（type=7）")
    api_params: Optional[Dict[str, Any]] = None
    js_code: Optional[str] = Field(None, description="JS 代码（type=8）")
    assert_text: Optional[str] = Field(None, description="断言文本内容")
    assert_img: Optional[str] = Field(None, description="断言图像路径")
    wait: Optional[float] = 1.0
    direction: Optional[str] = Field("down", description="滑动方向: up|down|left|right")
    distance: Optional[int] = Field(300, description="滑动距离(px)")


class RunScriptBody(BaseModel):
    id: int
    task_name: str = ""
    result_id: Optional[str] = None
    platform: str = "wechat"
    framework: str = "minium"
    platform_config: Optional[Dict[str, Any]] = None
    project_id: Optional[int] = Field(None, description="所属项目ID")


class StopScriptBody(BaseModel):
    result_id: str


class ResultListBody(BaseModel):
    page: int = 1
    pageSize: int = 10
    search: Dict[str, Any] = Field(default_factory=dict)
