# -*- coding: utf-8 -*-
# @author: rebort

from app.api.v1.Ntesterc_module.Ntesterc_task_scheduler.celery_worker.worker import celery


@celery.task
def add(i):
    return 1 + i
