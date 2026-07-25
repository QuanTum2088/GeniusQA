#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""
消息模型
"""
from sqlalchemy import Column, BigInteger, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.db_base import Base


class MessageModel(Base):
    """消息模型"""
    __tablename__ = "sys_message"
    __table_args__ = {"comment": "AI 消息表"}
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    conversation_id = Column(BigInteger, ForeignKey("sys_conversation.id"), nullable=False, index=True, comment="对话ID")
    role = Column(String(20), nullable=False, comment="角色（system/user/assistant）")
    content = Column(Text, nullable=False, comment="消息内容")
    message_type = Column(String(50), default="text", comment="消息类型")
    meta_data = Column("metadata", JSON, nullable=True, comment="元数据")
    tokens_used = Column(Integer, nullable=True, comment="使用的令牌数")
    
    # 关系
    conversation = relationship("ConversationModel", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, content={self.content[:50]}...)>"
