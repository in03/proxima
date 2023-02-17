#!/usr/bin/env python

import logging
import os
import sys

from celery import Celery

from proxima.settings.manager import settings

# QUEUE - Celery routing queue using version constraint key
celery_queue = os.getenv("PROXIMA_VC_KEY")
if not settings.app.version_constrain:
    celery_queue = "all"

logger = logging.getLogger("proxima")
logger.setLevel(settings.app.loglevel)

# Windows can't fork processes. It'll choke if you make it try.
if sys.platform == "win32":
    os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")

app = Celery("worker")

app.autodiscover_tasks(
    [
        "proxima.celery.tasks",
    ]
)

# Remap terms
broker_settings = {
    "broker_url": settings.broker.broker_url,
    "result_backend": settings.broker.broker_url,
    "result_expires": settings.broker.result_expires,
}

try:
    app.config_from_object(broker_settings)
except Exception as e:
    logger.error(
        f"[red]Couldn't configure Celery with settings {broker_settings}[/]\n{e}"
    )

# Fragile! Moved from user settings to here.
app.conf.update(
    result_extended=True,  # Allows us to get task args after task completion
    acks_late=True,
    worker_pool_restarts=True,
    # worker_send_task_events=True,
    worker_cancel_long_running_tasks_on_connection_loss=True,
    worker_hijack_root_logger=False,
    worker_redirect_stdouts=False,
    # 1 task per process at a time
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1,
)
