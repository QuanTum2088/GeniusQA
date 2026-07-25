#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LLMConfigCreateSchema(BaseModel):
    """创建 LLM 配置"""
    model_config = ConfigDict(protected_namespaces=())  # 允许 model_ 前缀
    
    config_name: str = Field(..., description="配置名称")
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    model_name: str = Field(..., description="模型名称（兼容）")
    api_key: Optional[str] = Field(None, description="API 密钥（本地模型如 Ollama 可为空）")
    base_url: Optional[str] = Field(None, description="API 基础URL")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    temperature: float = Field(0.7, description="温度参数")
    max_tokens: int = Field(2000, description="最大令牌数")
    supports_vision: bool = Field(False, description="是否支持多模态")
    context_limit: int = Field(128000, description="上下文限制")
    is_default: bool = Field(False, description="是否为默认配置")
    is_active: bool = Field(True, description="是否启用")


class LLMConfigUpdateSchema(BaseModel):
    """更新 LLM 配置"""
    model_config = ConfigDict(protected_namespaces=())  # 允许 model_ 前缀
    
    config_name: Optional[str] = Field(None, description="配置名称")
    name: Optional[str] = Field(None, description="模型名称")
    provider: Optional[str] = Field(None, description="提供商")
    model_name: Optional[str] = Field(None, description="模型名称（兼容）")
    api_key: Optional[str] = Field(None, description="API 密钥")
    base_url: Optional[str] = Field(None, description="API 基础URL")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    temperature: Optional[float] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大令牌数")
    supports_vision: Optional[bool] = Field(None, description="是否支持多模态")
    context_limit: Optional[int] = Field(None, description="上下文限制")
    is_default: Optional[bool] = Field(None, description="是否为默认配置")
    is_active: Optional[bool] = Field(None, description="是否启用")


class LLMConfigOutSchema(BaseModel):
    """LLM 配置输出"""
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    
    id: int
    config_name: str
    name: str
    provider: str
    model_name: str
    api_key: Optional[str]
    base_url: Optional[str]
    system_prompt: Optional[str]
    temperature: float
    max_tokens: int
    supports_vision: bool
    context_limit: int
    is_default: bool
    is_active: bool
    creation_date: Optional[str]
    created_by: Optional[int]
    updation_date: Optional[str]
    updated_by: Optional[int]


class LLMConfigTestSchema(BaseModel):
    """测试 LLM 配置"""
    model_config = ConfigDict(protected_namespaces=())  # 允许 model_ 前缀
    
    config_id: Optional[int] = Field(None, description="配置ID（如果提供则使用已保存的配置）")
    config_name: Optional[str] = Field(None, description="配置名称")
    name: Optional[str] = Field(None, description="模型名称")
    provider: Optional[str] = Field(None, description="提供商")
    api_key: Optional[str] = Field(None, description="API 密钥")
    base_url: Optional[str] = Field(None, description="API 基础URL")
    test_message: str = Field("Hello, this is a test message.", description="测试消息")


class LLMConfigTestResponseSchema(BaseModel):
    """测试响应"""
    success: bool
    message: str
    response: Optional[str] = None
    error: Optional[str] = None
    latency: Optional[float] = None  # 响应时间（秒）
