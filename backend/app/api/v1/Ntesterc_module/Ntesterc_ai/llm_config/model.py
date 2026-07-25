#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""
LLM 配置数据模型
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text
from sqlalchemy.orm import mapped_column, relationship
from app.core.db_base import Base


class LLMConfigModel(Base):
    """LLM 配置模型（支持全局配置）"""
    
    __tablename__ = "sys_llm_config"
    __table_args__ = {'comment': 'LLM 配置表', 'mysql_charset': 'utf8'}
    
    # 配置标识字段
    config_name = mapped_column(
        String(255), 
        nullable=False,
        comment="用户自定义的配置名称，如'生产环境OpenAI'、'测试Claude配置'"
    )
    
    # 模型信息
    name = mapped_column(String(100), nullable=False, comment="模型名称，如 gpt-4, claude-3-sonnet")
    provider = mapped_column(String(50), nullable=False, comment="LLM 提供商")  # openai, anthropic, ollama, custom
    model_name = mapped_column(String(100), nullable=False, comment="模型名称（兼容字段）")
    
    # API 配置
    api_key = mapped_column(String(500), nullable=True, comment="API 密钥（本地模型如 Ollama 可为空）")
    base_url = mapped_column(String(500), nullable=True, comment="API 基础URL")
    
    # 系统提示词
    system_prompt = mapped_column(
        Text,
        nullable=True,
        comment="指导LLM行为的系统级提示词"
    )
    
    # 模型参数
    temperature = mapped_column(Float, default=0.7, comment="温度参数")
    max_tokens = mapped_column(Integer, default=2000, comment="最大令牌数")
    
    # 多模态支持
    supports_vision = mapped_column(
        Boolean,
        default=False,
        comment="模型是否支持图片/多模态输入（如GPT-4V、Qwen-VL等）"
    )
    
    # 上下文限制
    context_limit = mapped_column(
        Integer,
        default=128000,
        comment="模型最大上下文Token数（GPT-4o: 128000, Claude: 200000, Gemini: 1000000）"
    )
    
    # 状态字段
    is_default = mapped_column(Boolean, default=False, comment="是否为默认配置")
    is_active = mapped_column(Boolean, default=True, comment="是否启用")
    
    # 关系
    conversations = relationship("ConversationModel", back_populates="llm_config")
    
    def __repr__(self):
        return f'<LLMConfig {self.config_name} ({self.provider})>'
