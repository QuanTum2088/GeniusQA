#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: Lucas
from fastapi import APIRouter

from app.api.v1.Ntesterc_module.Ntesterc_performance.config.controller import router as config_router
from app.api.v1.Ntesterc_module.Ntesterc_performance.files.controller import router as files_router
from app.api.v1.Ntesterc_module.Ntesterc_performance.report.controller import router as report_router
from app.api.v1.Ntesterc_module.Ntesterc_performance.scenario.controller import router as scenario_router
from app.api.v1.Ntesterc_module.Ntesterc_performance.scheduler.controller import router as scheduler_router

router = APIRouter()
router.include_router(config_router)
router.include_router(files_router)
router.include_router(scenario_router)
router.include_router(scheduler_router)
router.include_router(report_router)