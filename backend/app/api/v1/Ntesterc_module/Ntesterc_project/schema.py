#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from app.core.base_schema import BaseSchema, PageQuerySchema, TimestampSchema


# ========== 项目 ==========
class ProjectBaseSchema(BaseSchema):
    """项目基础Schema"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    status: Optional[str] = Field("active", description="状态")


class ProjectCreateSchema(ProjectBaseSchema):
    """项目创建Schema"""
    pass


class ProjectUpdateSchema(BaseSchema):
    """项目更新Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectOutSchema(ProjectBaseSchema, TimestampSchema):
    """项目输出Schema"""
    id: int
    owner_id: int
    owner_name: Optional[str] = None  # 项目负责人姓名
    creation_date: datetime
    updation_date: datetime
    member_count: Optional[int] = 0
    environment_count: Optional[int] = 0


class ProjectQuerySchema(PageQuerySchema):
    """项目查询Schema"""
    name: Optional[str] = Field(None, description="项目名称")
    status: Optional[str] = Field(None, description="项目状态")


# ========== 项目成员 ==========
class ProjectMemberBaseSchema(BaseSchema):
    """项目成员基础Schema"""
    user_id: int = Field(..., description="用户ID")
    role: str = Field("tester", description="角色")


class ProjectMemberCreateSchema(ProjectMemberBaseSchema):
    """项目成员创建Schema"""
    pass


class ProjectMemberUpdateSchema(BaseSchema):
    """项目成员更新Schema"""
    role: str = Field(..., description="角色")


class ProjectMemberOutSchema(ProjectMemberBaseSchema, TimestampSchema):
    """项目成员输出Schema"""
    id: int
    project_id: int
    username: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    creation_date: datetime


# ========== 项目环境 ==========
class ProjectEnvironmentBaseSchema(BaseSchema):
    """项目环境基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="环境名称")
    base_url: Optional[str] = Field(None, max_length=500, description="基础URL")
    description: Optional[str] = Field(None, description="环境描述")
    variables: Optional[Dict[str, Any]] = Field(None, description="环境变量")
    is_default: Optional[bool] = Field(False, description="是否默认")


class ProjectEnvironmentCreateSchema(ProjectEnvironmentBaseSchema):
    """项目环境创建Schema"""
    pass


class ProjectEnvironmentUpdateSchema(BaseSchema):
    """项目环境更新Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    base_url: Optional[str] = None
    description: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None


class ProjectEnvironmentOutSchema(ProjectEnvironmentBaseSchema, TimestampSchema):
    """项目环境输出Schema"""
    id: int
    project_id: int
    creation_date: datetime
