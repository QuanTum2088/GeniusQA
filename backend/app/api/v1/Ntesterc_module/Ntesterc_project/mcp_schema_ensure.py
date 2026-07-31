#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

"""确保 projects / project_mcp_config 新增列存在（兼容未跑 alembic 的环境）。"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
_ensured = False


async def ensure_mcp_schema(db: AsyncSession) -> None:
    global _ensured
    if _ensured:
        return
    stmts = [
        "ALTER TABLE projects ADD COLUMN workspace_path VARCHAR(2000) NULL COMMENT '本机工作目录'",
        "ALTER TABLE project_mcp_config ADD COLUMN project_id BIGINT NULL COMMENT '绑定项目'",
        "ALTER TABLE project_mcp_config ADD COLUMN scope VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '作用域'",
        "ALTER TABLE project_mcp_config MODIFY COLUMN url VARCHAR(2048) NULL COMMENT 'MCP URL'",
        "ALTER TABLE project_mcp_config ADD COLUMN command VARCHAR(500) NULL COMMENT 'stdio 命令'",
        "ALTER TABLE project_mcp_config ADD COLUMN args JSON NULL COMMENT 'stdio 参数'",
        "ALTER TABLE project_mcp_config ADD COLUMN env JSON NULL COMMENT 'stdio 环境变量'",
        "ALTER TABLE project_mcp_config ADD COLUMN auth_type VARCHAR(30) NULL DEFAULT 'none' COMMENT '鉴权类型'",
        "ALTER TABLE project_mcp_config ADD COLUMN auth_config JSON NULL COMMENT '鉴权参数'",
        "ALTER TABLE project_mcp_config ADD COLUMN description TEXT NULL COMMENT '备注'",
        "ALTER TABLE project_mcp_config ADD COLUMN is_connected TINYINT(1) NOT NULL DEFAULT 0 COMMENT '最近一次测试是否已连接'",
        "UPDATE project_mcp_config SET scope='user' WHERE scope IS NULL OR scope=''",
    ]
    for sql in stmts:
        try:
            await db.execute(text(sql))
            await db.commit()
        except Exception as e:
            await db.rollback()
            msg = str(e).lower()
            if "duplicate" in msg or "exists" in msg or "1060" in msg:
                continue
            logger.debug(f"ensure_mcp_schema skip: {e}")
    _ensured = True
