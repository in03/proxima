#!/usr/bin/env python

# Celery settings should be configured using celery setting or environment variables.
# See the .env-sample if using Docker, or celery_settings-sample.py if running in virtual env.

from __future__ import absolute_import

import os
import sys

from celery import Celery
from resolve_proxy_encoder.settings.manager import SettingsManager

config = SettingsManager()

# Windows can't fork processes. It'll choke if you make it try.
if sys.platform == "win32":
    os.environ.setdefault("FORKED_BY_MULTIPROCESSING", "1")

app = Celery("worker")

app.autodiscover_tasks(
    [
        "resolve_proxy_encoder.worker.tasks.standard_encode",
        "resolve_proxy_encoder.worker.tasks.chunked_encode",
    ]
)

try:
    app.config_from_object(config["celery_settings"])
except Exception as e:
    raise Exception("Couldn't load settings from YAML!")

# Fragile! Moved from user settings to here.
app.conf.update(
    task_serializer="json",  # Pickle allows us to post-encode link using remote objects
    result_serializer="json",  # Keep same as above
    result_extended=True,  # Allows us to get task args after task completion
    acks_late=True,
    accept_content=["json", "pickle", "application/x-python-serialize"],
    result_accept_content=["json", "pickle", "application/x-python-serialize"],
    worker_pool_restarts=True,
    worker_send_task_events=True,
    worker_cancel_long_running_tasks_on_connection_loss=True,
)
