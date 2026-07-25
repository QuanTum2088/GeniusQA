#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, BigInteger
from sqlalchemy.sql import func
from app.core.db_base import Base


class DesktopMenuModel(Base):
    """脚本菜单（目录树）"""
    __tablename__ = "desktop_menus"
    __table_args__ = {"comment": "客户端UI自动化菜单表"}

    name       = Column(String(255), nullable=False, comment="名称")
    pid        = Column(BigInteger, nullable=False, default=0, comment="父ID，0为根")
    type       = Column(Integer, nullable=False, default=0, comment="0=目录 1=脚本组 2=脚本")
    user_id    = Column(BigInteger, nullable=False, comment="用户ID")
    project_id = Column(BigInteger, nullable=True, comment="所属项目ID")


class DesktopScriptModel(Base):
    """脚本内容"""
    __tablename__ = "desktop_scripts"
    __table_args__ = {"comment": "客户端UI自动化脚本表"}

    menu_id     = Column(BigInteger, nullable=False, unique=True, comment="菜单ID")
    framework   = Column(String(64), nullable=False, default="pywinauto",
                         comment="执行框架: pywinauto | pyautogui | winappdriver | sikuli")
    script      = Column(JSON, nullable=False, default=list, comment="步骤列表")
    user_id     = Column(BigInteger, nullable=False, comment="用户ID")
    create_time = Column(DateTime, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class DesktopResultListModel(Base):
    """执行任务汇总"""
    __tablename__ = "desktop_result_lists"
    __table_args__ = {"comment": "客户端UI自动化执行汇总表"}

    task_name     = Column(String(255), nullable=False, comment="任务名称")
    result_id     = Column(String(255), unique=True, nullable=False, comment="执行ID")
    framework     = Column(String(64), nullable=False, default="pywinauto", comment="执行框架")
    script_list   = Column(JSON, nullable=False, default=list, comment="脚本列表")
    script_status = Column(JSON, nullable=False, default=list, comment="执行状态")
    project_id    = Column(BigInteger, nullable=True, comment="所属项目ID")
    start_time    = Column(DateTime, server_default=func.now(), comment="开始时间")
    end_time      = Column(DateTime, nullable=True, comment="结束时间")
    user_id       = Column(BigInteger, nullable=False, comment="用户ID")


class DesktopResultModel(Base):
    """单步执行结果"""
    __tablename__ = "desktop_results"
    __table_args__ = {"comment": "客户端UI自动化步骤结果表"}

    result_id    = Column(String(255), nullable=False, comment="执行ID")
    menu_id      = Column(BigInteger, nullable=False, comment="菜单ID")
    name         = Column(String(255), nullable=False, comment="步骤名称")
    status       = Column(Integer, nullable=False, comment="0=失败 1=成功 2=进行中")
    log          = Column(Text, nullable=True, comment="日志")
    before_img   = Column(Text, nullable=True, comment="执行前截图")
    after_img    = Column(Text, nullable=True, comment="执行后截图")
    assert_value = Column(JSON, nullable=True, comment="断言详情")
    create_time  = Column(DateTime, server_default=func.now(), comment="执行时间")
    user_id      = Column(BigInteger, nullable=False, comment="用户ID")
