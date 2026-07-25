#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Text, Integer, JSON, Boolean, Index, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db_base import Base


class ModuleInfoModel(Base):
    """测试模块信息模型"""
    __tablename__ = 'module_info'
    __table_args__ = (
        Index("idx_module_project", "project_id"),
        Index("idx_module_parent", "parent_id"),
        {'comment': '测试模块信息表', 'mysql_charset': 'utf8mb4'}
    )
    
    name = Column(String(100), nullable=False, comment='模块名称')
    project_id = Column(Integer, nullable=False, comment='所属项目ID')
    parent_id = Column(BigInteger, nullable=True, comment='父模块ID')
    description = Column(Text, nullable=True, comment='模块描述')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    
    def __repr__(self):
        try:
            # 使用 __dict__ 直接访问属性，避免触发延迟加载
            id_val = self.__dict__.get('id', 'N/A')
            name_val = self.__dict__.get('name', 'N/A')
            project_id_val = self.__dict__.get('project_id', 'N/A')
            parent_id_val = self.__dict__.get('parent_id', 'N/A')
            return f"<ModuleInfo(id={id_val}, name='{name_val}', project_id={project_id_val}, parent_id={parent_id_val})>"
        except:
            return f"<ModuleInfo(detached)>"


class TestCaseModel(Base):
    """测试用例模型"""
    
    __tablename__ = "test_cases"
    __table_args__ = (
        Index("idx_testcase_project", "project_id"),
        Index("idx_testcase_author", "author_id"),
        Index("idx_testcase_status", "status"),
        {'comment': '测试用例表', 'mysql_charset': 'utf8mb4'}
    )
    
    project_id = Column(BigInteger, nullable=False, comment="项目ID")
    module_id = Column(BigInteger, ForeignKey("module_info.id", use_alter=True, name="fk_testcase_module"), nullable=True, comment="模块ID")
    title = Column(String(500), nullable=False, comment="用例标题")
    description = Column(Text, comment="用例描述")
    preconditions = Column(Text, comment="前置条件")
    expected_result = Column(Text, comment="预期结果")
    priority = Column(String(20), default="medium", comment="优先级: low/medium/high/critical")
    status = Column(String(20), default="draft", comment="状态: draft/active/deprecated")
    test_type = Column(String(20), default="functional", comment="类型: functional/integration/api/ui/performance/security")
    tags = Column(JSON, comment="标签")
    author_id = Column(BigInteger, ForeignKey("sys_user.id", use_alter=True, name="fk_testcase_author"), nullable=False, comment="作者ID")
    assignee_id = Column(BigInteger, ForeignKey("sys_user.id", use_alter=True, name="fk_testcase_assignee"), comment="指派人ID")
    
    # 关系定义
    steps = relationship("TestCaseStepModel", back_populates="test_case", lazy="select", order_by="TestCaseStepModel.step_number")
    author = relationship("app.api.v1.system.user.model.UserModel", foreign_keys=[author_id], lazy="select")
    assignee = relationship("app.api.v1.system.user.model.UserModel", foreign_keys=[assignee_id], lazy="select")
    versions = relationship("TestCaseVersionModel", back_populates="test_case", lazy="select")
    module = relationship("ModuleInfoModel", foreign_keys=[module_id], lazy="select")


class TestCaseStepModel(Base):
    """测试用例步骤模型"""
    
    __tablename__ = "test_case_steps"
    __table_args__ = (
        Index("idx_step_case", "test_case_id"),
        {'comment': '测试用例步骤表', 'mysql_charset': 'utf8mb4'}
    )
    
    test_case_id = Column(BigInteger, ForeignKey("test_cases.id"), nullable=False, comment="测试用例ID")
    step_number = Column(Integer, nullable=False, comment="步骤序号")
    action = Column(Text, nullable=False, comment="操作")
    expected = Column(Text, nullable=False, comment="预期结果")
    
    # 关系定义
    test_case = relationship("TestCaseModel", back_populates="steps")


class VersionModel(Base):
    """版本模型"""
    
    __tablename__ = "versions"
    __table_args__ = (
        Index("idx_version_baseline", "is_baseline"),
        {'comment': '版本表', 'mysql_charset': 'utf8mb4'}
    )
    
    name = Column(String(100), nullable=False, comment="版本名称")
    description = Column(Text, comment="版本描述")
    is_baseline = Column(Boolean, default=False, comment="是否基线版本")
    
    # 关系定义
    projects = relationship("ProjectVersionModel", back_populates="version", lazy="select")
    test_cases = relationship("TestCaseVersionModel", back_populates="version", lazy="select")


class ProjectVersionModel(Base):
    """项目版本关联模型"""
    
    __tablename__ = "project_versions"
    __table_args__ = (
        Index("idx_pv_project", "project_id"),
        Index("idx_pv_version", "version_id"),
        {'comment': '项目版本关联表', 'mysql_charset': 'utf8mb4'}
    )
    
    project_id = Column(BigInteger, nullable=False, comment="项目ID")
    version_id = Column(BigInteger, ForeignKey("versions.id"), nullable=False, comment="版本ID")
    
    # 关系定义
    version = relationship("VersionModel", back_populates="projects", lazy="select")


class TestCaseVersionModel(Base):
    """用例版本关联模型"""
    
    __tablename__ = "test_case_versions"
    __table_args__ = (
        Index("idx_tcv_case", "test_case_id"),
        Index("idx_tcv_version", "version_id"),
        {'comment': '用例版本关联表', 'mysql_charset': 'utf8mb4'}
    )
    
    test_case_id = Column(BigInteger, ForeignKey("test_cases.id"), nullable=False, comment="测试用例ID")
    version_id = Column(BigInteger, ForeignKey("versions.id"), nullable=False, comment="版本ID")
    
    # 关系定义
    test_case = relationship("TestCaseModel", back_populates="versions")
    version = relationship("VersionModel", back_populates="test_cases", lazy="select")
