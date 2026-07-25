#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Integer, UniqueConstraint
from sqlalchemy.orm import mapped_column
from app.core.db_base import Base


class CodeSequenceModel(Base):
    """编码序号表，用于存储各业务类型的序号"""
    
    __tablename__ = "sys_code_sequence"
    __table_args__ = (
        UniqueConstraint('business_type', 'prefix', 'date_key', name='uk_business_prefix_date'),
        {'comment': '编码序号表', 'mysql_charset': 'utf8'}
    )
    
    business_type = mapped_column(String(100), nullable=False, comment="业务类型")
    prefix = mapped_column(String(50), default='', comment="前缀")
    date_key = mapped_column(String(20), default='', comment="日期键（用于按日期重置）")
    current_seq = mapped_column(Integer, default=0, comment="当前序号")
    
    def __repr__(self):
        return f'<CodeSequence {self.business_type}-{self.prefix}-{self.date_key}: {self.current_seq}>'
