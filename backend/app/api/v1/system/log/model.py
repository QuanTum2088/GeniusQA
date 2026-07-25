#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Integer, BigInteger, DateTime, Text, JSON
from app.core.db_base import Base


class OperationLogModel(Base):
    """操作日志模型"""
    
    __tablename__ = "sys_operation_log"
    __table_args__ = {'comment': '操作日志表'}
    
    user_id = Column(BigInteger, nullable=True, comment="操作用户ID")
    username = Column(String(64), nullable=True, comment="操作用户名")
    operation = Column(String(100), nullable=False, comment="操作类型")
    method = Column(String(10), nullable=False, comment="请求方法")
    url = Column(String(500), nullable=False, comment="请求URL")
    ip = Column(String(50), nullable=True, comment="操作IP")
    location = Column(String(200), nullable=True, comment="操作地点")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    
    module = Column(String(100), nullable=True, comment="操作模块")
    description = Column(String(500), nullable=True, comment="操作描述")
    request_data = Column(JSON, nullable=True, comment="请求参数")
    response_data = Column(JSON, nullable=True, comment="响应数据")
    
    status = Column(Integer, nullable=False, default=1, comment="操作状态（0:失败 1:成功）")
    error_msg = Column(Text, nullable=True, comment="错误信息")
    execution_time = Column(Integer, nullable=True, comment="执行时间(毫秒)")
    
    operation_time = Column(DateTime, nullable=False, comment="操作时间")


class LoginLogModel(Base):
    """登录日志模型"""
    
    __tablename__ = "sys_login_log"
    __table_args__ = {'comment': '登录日志表'}
    
    user_id = Column(BigInteger, nullable=True, comment="用户ID")
    username = Column(String(64), nullable=False, comment="用户名")
    login_type = Column(String(20), nullable=False, default="web", comment="登录类型")
    
    ip = Column(String(50), nullable=True, comment="登录IP")
    location = Column(String(200), nullable=True, comment="登录地点")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    browser = Column(String(100), nullable=True, comment="浏览器")
    os = Column(String(100), nullable=True, comment="操作系统")
    
    status = Column(Integer, nullable=False, comment="登录状态（0:失败 1:成功）")
    message = Column(String(500), nullable=True, comment="登录信息")
    
    login_time = Column(DateTime, nullable=False, comment="登录时间")
    logout_time = Column(DateTime, nullable=True, comment="退出时间")
