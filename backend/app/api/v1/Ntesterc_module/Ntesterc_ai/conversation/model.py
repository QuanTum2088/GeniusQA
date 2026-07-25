#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""
对话模型
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db_base import Base


class ConversationModel(Base):
    """对话模型"""
    __tablename__ = "sys_conversation"
    __table_args__ = {"comment": "AI 对话表"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    session_id = Column(String(255), nullable=False, unique=True, index=True, comment="会话ID")
    title = Column(String(255), nullable=True, comment="对话标题")
    llm_config_id = Column(BigInteger, ForeignKey("sys_llm_config.id"), nullable=True, comment="LLM配置ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    is_active = Column(Integer, default=1, comment="是否活跃（1是 0否）")
    
    # 关系
    llm_config = relationship("LLMConfigModel", back_populates="conversations")
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id}, title={self.title})>"
