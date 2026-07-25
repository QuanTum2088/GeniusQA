# -*- coding: utf-8 -*-
# @author: rebort
"""
Celery CLI 短入口

  celery -A celery_app.celery worker --pool=solo -l INFO
  celery -A celery_app.celery beat -l INFO
"""
from app.api.v1.Ntesterc_module.Ntesterc_task_scheduler.celery_worker.worker import celery

__all__ = ["celery"]
