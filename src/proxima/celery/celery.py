#!/usr/bin/env python

import logging
import os
import sys
from functools import lru_cache

from pathlib import Path
from celery import Celery
from proxima.settings import settings
from proxima.app.package import build_info
import proxima

logger = logging.getLogger("proxima")
logger.setLevel(settings["app"]["loglevel"])

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
    "broker_url": settings["broker"]["url"],
    "result_backend": settings["broker"]["url"],
    "result_expires": settings["broker"]["result_expires"],
}

try:
    app.config_from_object(broker_settings)
except Exception as e:
    logger.error(f"[red]Couldn't load settings from YAML![/]\n{e}")

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


@lru_cache
def get_version_constraint_key() -> str:

    # TODO: IMPORTANT! Make this path resolution more robust
    # These paths are relative and depend on both source and Pip installation structure not changing
    logger.debug("[cyan]Getting version constraint key")

    if build_info.get_build_info:
        vc_key_file = Path(proxima.__file__).parent.parent.parent.joinpath(
            "version_constraint_key"
        )
        logger.debug("[magenta] * Using source path")

    else:
        logger.debug("[magenta] * Using package path")
        vc_key_file = Path(proxima.__file__).parent.parent.joinpath(
            "version_constraint_key"
        )
        logger.debug(f"[magenta] * vc_key_file path: {vc_key_file}")

    with open(vc_key_file) as file:
        vc_key = file.read()
        logger.debug(f"[magenta] * vc_key value: {vc_key}")
        return vc_key


def get_queue() -> str:
    """Get Celery queue name (routing key) from version constraint key

    Allows constraining tasks and workers to exact same version and prevent breaking changes.
    """

    if settings["app"]["disable_version_constrain"]:
        return "all"

    return get_version_constraint_key()
