#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""
LLM 用量日志模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text
from app.core.db_base import Base


class LLMUsageLogModel(Base):
    """LLM 调用用量日志"""

    __tablename__ = "llm_usage_logs"
    __table_args__ = {"comment": "LLM 用量日志表"}

    user_id = Column(BigInteger, nullable=True, index=True, comment="用户ID")
    llm_config_id = Column(BigInteger, nullable=True, index=True, comment="LLM配置ID")
    provider = Column(String(50), nullable=True, comment="提供商")
    model_name = Column(String(100), nullable=True, index=True, comment="模型名称")
    source = Column(String(50), nullable=False, default="chat", index=True, comment="来源 chat/browser_use 等")
    conversation_id = Column(BigInteger, nullable=True, index=True, comment="对话ID")
    message_id = Column(BigInteger, nullable=True, comment="消息ID")
    prompt_tokens = Column(Integer, nullable=False, default=0, comment="输入 token")
    completion_tokens = Column(Integer, nullable=False, default=0, comment="输出 token")
    total_tokens = Column(Integer, nullable=False, default=0, comment="总 token")
    cached_tokens = Column(Integer, nullable=False, default=0, comment="缓存命中 token")
    status = Column(String(20), nullable=False, default="success", comment="success/error")
    error_message = Column(Text, nullable=True, comment="错误信息")
    latency_ms = Column(Integer, nullable=True, comment="耗时毫秒")
