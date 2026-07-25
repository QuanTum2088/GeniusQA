#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
"""
API v1：基座（system/common/monitor）+ 业务（Ntesterc_module）
"""

from fastapi import APIRouter

from app.api.v1.system import router as system_router
from app.api.v1.monitor import router as monitor_router
from app.api.v1.common.health.controller import router as health_router
from app.api.v1.Ntesterc_module import router as ntesterc_biz_router

router = APIRouter(prefix="/v1")

# ---------- 基座 ----------
router.include_router(system_router, prefix="/system", tags=["系统管理"])
router.include_router(monitor_router, prefix="/monitor", tags=["系统监控"])
router.include_router(health_router, prefix="/common/health", tags=["健康检查"])

# ---------- 业务（URL 形如 /v1/Ntesterc_* ）----------
router.include_router(ntesterc_biz_router)

__all__ = ["router"]
