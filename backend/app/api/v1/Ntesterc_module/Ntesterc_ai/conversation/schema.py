#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


# ==================== 对话相关 ====================

class ConversationCreateRequest(BaseModel):
    """创建对话请求"""
    title: Optional[str] = Field(None, description="对话标题")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID（不指定则使用默认配置）")


class ConversationUpdateRequest(BaseModel):
    """更新对话请求"""
    title: Optional[str] = Field(None, description="对话标题")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")
    is_active: Optional[bool] = Field(None, description="是否活跃")


class ConversationData(BaseModel):
    """对话数据"""
    id: int
    session_id: str
    title: Optional[str]
    llm_config_id: Optional[int]
    user_id: int
    is_active: bool
    creation_date: datetime
    updation_date: datetime
    message_count: Optional[int] = Field(None, description="消息数量")
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """对话列表响应"""
    conversations: List[ConversationData]
    total: int


# ==================== 消息相关 ====================

class MessageData(BaseModel):
    """消息数据"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: int
    conversation_id: int
    role: str
    content: str
    message_type: str
    meta_data: Optional[Dict[str, Any]] = Field(None, serialization_alias="metadata")
    tokens_used: Optional[int]
    creation_date: datetime


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    content: str = Field(..., description="消息内容")
    stream: bool = Field(False, description="是否流式响应")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="附件列表")
    project_id: Optional[int] = Field(None, description="项目ID")
    use_knowledge_base: bool = Field(False, description="是否启用知识库检索")
    knowledge_base_id: Optional[int] = Field(None, description="知识库ID")
    use_mcp: bool = Field(False, description="是否启用MCP工具")
    mcp_config_id: Optional[int] = Field(None, description="MCP配置ID")
    use_skill: bool = Field(False, description="是否启用Skill工具")
    skill_id: Optional[int] = Field(None, description="Skill ID（智能模式默认工具）")
    tool_mode: str = Field("smart", description="工具模式：smart(智能) / direct(直连)")
    tool_provider: Optional[str] = Field(None, description="直连模式工具提供方：mcp/skill")
    tool_name: Optional[str] = Field(None, description="直连模式工具名称")
    tool_arguments: Optional[Dict[str, Any]] = Field(None, description="直连模式工具参数")
    tool_session_id: Optional[str] = Field(None, description="直连模式会话ID（预留给Skill会话化执行）")

    @field_validator("use_knowledge_base", "use_mcp", mode="before")
    @classmethod
    def coerce_bool_flags(cls, v):
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return v != 0
        if isinstance(v, str):
            return v.strip().lower() in ("1", "true", "yes", "on")
        return bool(v)

    @field_validator("tool_mode", mode="before")
    @classmethod
    def normalize_tool_mode(cls, v):
        val = str(v or "smart").strip().lower()
        return val if val in ("smart", "direct") else "smart"

    @field_validator("tool_provider", mode="before")
    @classmethod
    def normalize_tool_provider(cls, v):
        if v is None:
            return None
        val = str(v).strip().lower()
        return val if val in ("mcp", "skill") else None


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    user_message: MessageData
    assistant_message: MessageData
    total_tokens: Optional[int] = None


class MessageListResponse(BaseModel):
    """消息列表响应"""
    messages: List[MessageData]
    total: int


# ==================== 流式响应 ====================

class StreamChunk(BaseModel):
    """流式响应块"""
    content: str
    done: bool = False
