#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort

from fastapi import APIRouter
from .controller import router as http_router
from .websocket import router as ws_router

# 合并路由
router = APIRouter()
router.include_router(http_router)
router.include_router(ws_router)

__all__ = ['router']
