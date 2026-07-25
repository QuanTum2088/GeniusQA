#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Index, Integer, JSON, String, Text, func

from app.core.db_base import Base


class SkillExecutionJobModel(Base):
    __tablename__ = "skill_execution_job"
    __table_args__ = (
        Index("idx_sej_project", "project_id"),
        Index("idx_sej_user", "user_id"),
        Index("idx_sej_skill", "skill_id"),
        Index("idx_sej_status", "status"),
        {"comment": "Skill执行任务表", "mysql_charset": "utf8mb4"},
    )

    project_id = Column(BigInteger, nullable=False, comment="项目ID")
    user_id = Column(BigInteger, nullable=False, comment="用户ID")
    skill_id = Column(BigInteger, ForeignKey("project_skill.id", use_alter=True, name="fk_sej_skill"), nullable=False)

    # action/command
    action_name = Column(String(120), nullable=True, comment="动作名（如 template/agent-browser-open）")
    command = Column(Text, nullable=True, comment="最终执行命令（runner执行）")
    input_args = Column(JSON, nullable=True, comment="输入参数（表单/高级JSON合并后）")
    session_id = Column(String(120), nullable=True, comment="会话ID（用于持久化浏览器/复用上下文）")

    # status lifecycle: pending/running/succeeded/failed/cancelled
    status = Column(String(30), nullable=False, default="pending", comment="状态")
    queued_at = Column(DateTime, default=func.now(), comment="入队时间")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    finished_at = Column(DateTime, nullable=True, comment="结束时间")

    return_code = Column(Integer, nullable=True, comment="返回码")
    stdout = Column(Text, nullable=True, comment="标准输出（截断）")
    stderr = Column(Text, nullable=True, comment="错误输出（截断）")
    error_message = Column(Text, nullable=True, comment="错误信息（非进程stderr）")

    runtime_key = Column(String(120), nullable=False, comment="runtime目录key（用于产物路径）")
    runner_type = Column(String(30), nullable=False, default="local", comment="runner类型 local/docker")
    runner_meta = Column(JSON, nullable=True, comment="runner元信息（镜像/容器id/节点等）")


class SkillExecutionEventModel(Base):
    __tablename__ = "skill_execution_event"
    __table_args__ = (
        Index("idx_see_job", "job_id"),
        Index("idx_see_job_seq", "job_id", "seq"),
        {"comment": "Skill执行事件流（日志）", "mysql_charset": "utf8mb4"},
    )

    job_id = Column(BigInteger, ForeignKey("skill_execution_job.id", use_alter=True, name="fk_see_job"), nullable=False)
    seq = Column(Integer, nullable=False, comment="事件序号（单job递增）")
    level = Column(String(20), nullable=False, default="info", comment="级别")
    message = Column(Text, nullable=False, comment="事件内容")
    ts = Column(DateTime, default=func.now(), comment="事件时间")


class SkillExecutionArtifactModel(Base):
    __tablename__ = "skill_execution_artifact"
    __table_args__ = (
        Index("idx_sea_job", "job_id"),
        Index("idx_sea_job_kind", "job_id", "kind"),
        {"comment": "Skill执行产物索引", "mysql_charset": "utf8mb4"},
    )

    job_id = Column(BigInteger, ForeignKey("skill_execution_job.id", use_alter=True, name="fk_sea_job"), nullable=False)
    kind = Column(String(20), nullable=False, comment="screenshots/artifacts")
    name = Column(String(255), nullable=False, comment="文件名")
    relative_path = Column(String(1200), nullable=False, comment="相对路径")
    size = Column(BigInteger, nullable=True, comment="大小")
    content_type = Column(String(120), nullable=True, comment="类型（可选）")
    is_deleted = Column(Boolean, default=False, comment="是否已删除")

