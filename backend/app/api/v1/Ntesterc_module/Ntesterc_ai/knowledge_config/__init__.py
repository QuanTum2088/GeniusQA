#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Rebort
from fastapi import APIRouter
from .controller import router as knowledge_config_router

router = APIRouter()
router.include_router(knowledge_config_router)

__all__ = ["router"]
