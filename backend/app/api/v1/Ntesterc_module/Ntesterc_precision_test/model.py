#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Integer, Text, JSON, BigInteger

from app.core.db_base import Base


class NtestRepositoryModel(Base):
    """Git 仓库信息表"""
    __tablename__ = 'ntest_repository'

    name = Column(String(64), nullable=False, index=True, comment='仓库名称')
    html_url = Column(String(255), nullable=False, comment='仓库地址（Git URL）')
    description = Column(Text, nullable=True, comment='仓库描述')
    service_id = Column(BigInteger, nullable=False, index=True, comment='关联 API 服务 ID')
    # 方案 B 预留：JaCoCo agent 连接信息
    service_host = Column(String(255), nullable=True, comment='服务部署地址（IP/域名），用于 jacoco dump')
    jacoco_port = Column(Integer, default=6300, comment='JaCoCo agent TCP 端口，默认 6300')
    lang_type = Column(String(32), default='java', comment='语言类型: java / python / javascript / go')
    # Inherited from Base: id, creation_date, created_by, updation_date, updated_by, enabled_flag, trace_id


class NtestCoverageReportModel(Base):
    """覆盖率报告元数据表"""
    __tablename__ = 'ntest_coverage_report'

    name = Column(String(64), nullable=False, index=True, comment='报告名称')
    service_id = Column(BigInteger, nullable=False, index=True, comment='关联 API 服务 ID')
    repo_id = Column(BigInteger, nullable=False, comment='关联仓库 ID')
    coverage_type = Column(Integer, nullable=False, comment='覆盖类型: 10=全量, 20=增量')
    coverage_rate = Column(String(20), nullable=True, comment='覆盖率, 如 "85.3%"')
    new_branches = Column(String(255), nullable=True, comment='新分支')
    new_last_commit_id = Column(String(255), nullable=True, comment='新 Commit ID')
    old_branches = Column(String(255), nullable=True, comment='旧分支 (增量模式)')
    old_last_commit_id = Column(String(255), nullable=True, comment='旧 Commit ID (增量模式)')
    package_count = Column(Integer, default=0, comment='包数量')
    class_count = Column(Integer, default=0, comment='类数量')
    method_count = Column(Integer, default=0, comment='方法数量')
    # Inherited from Base: id, creation_date, created_by, updation_date, updated_by, enabled_flag, trace_id


class NtestCoverageDetailModel(Base):
    """覆盖率详情表 (包/类/方法级别)"""
    __tablename__ = 'ntest_coverage_detail'

    # Scope identifiers
    report_id = Column(BigInteger, nullable=False, index=True, comment='关联报告 ID')
    package_name = Column(String(255), nullable=True, index=True, comment='包名')
    class_name = Column(String(255), nullable=True, comment='类名')
    class_file_content = Column(Text, nullable=True, comment='类源代码内容')
    class_source_path = Column(String(255), nullable=True, comment='源文件路径')
    class_md5 = Column(String(255), nullable=True, comment='源文件 MD5')

    # Class-level coverage counters
    class_missed = Column(Integer, default=0, comment='类未覆盖数')
    class_covered = Column(Integer, default=0, comment='类已覆盖数')

    # Method details (stored as JSON array)
    methods = Column(JSON, nullable=True, comment='方法覆盖详情列表 (JSON)')

    # Class-level aggregated counters (summed from methods)
    branch_missed = Column(Integer, default=0)
    branch_covered = Column(Integer, default=0)
    instruction_missed = Column(Integer, default=0)
    instruction_covered = Column(Integer, default=0)
    line_missed = Column(Integer, default=0)
    line_covered = Column(Integer, default=0)
    method_missed = Column(Integer, default=0)
    method_covered = Column(Integer, default=0)
    # Inherited from Base: id, creation_date, created_by, updation_date, updated_by, enabled_flag, trace_id
