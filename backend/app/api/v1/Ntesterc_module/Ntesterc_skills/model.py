#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import Column, String, Text, JSON, Boolean, Index, BigInteger, ForeignKey
from app.core.db_base import Base


class ProjectSkillModel(Base):
    """项目技能配置（来源：内置/Git/本地上传）"""

    __tablename__ = "project_skill"
    __table_args__ = (
        Index("idx_project_skill_project", "project_id"),
        Index("idx_project_skill_user", "user_id"),
        Index("uq_project_skill_user_project_name", "user_id", "project_id", "name", unique=True),
        {"comment": "项目技能表", "mysql_charset": "utf8mb4"},
    )

    project_id = Column(BigInteger, ForeignKey("projects.id", use_alter=True, name="fk_ps_project"), nullable=False, comment="项目ID")
    user_id = Column(BigInteger, ForeignKey("sys_user.id", use_alter=True, name="fk_ps_user"), nullable=False, comment="所属用户")
    name = Column(String(255), nullable=False, comment="技能名称")
    description = Column(Text, nullable=True, comment="技能描述")
    scenario_category = Column(String(100), nullable=True, comment="场景分类，如agent-browser-skill")
    source_type = Column(String(30), nullable=False, default="builtin", comment="来源类型 builtin/github/gitee/upload")
    repo_url = Column(String(2048), nullable=True, comment="仓库URL")
    skill_path = Column(String(2000), nullable=True, comment="技能本地目录")
    entry_command = Column(String(500), nullable=True, comment="执行命令")
    is_active = Column(Boolean, default=True, comment="是否启用")
    extra_config = Column(JSON, nullable=True, comment="附加配置")

