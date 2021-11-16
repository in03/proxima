#!/usr/bin/env python

# Celery settings should be configured using celery setting or environment variables.
# See the .env-sample if using Docker, or celery_settings-sample.py if running in virtual env. 

from __future__ import absolute_import
from celery import Celery

import os
import sys

from resolve_proxy_encoder.settings import app_settings
config = app_settings.get_user_settings()


# Windows can't fork processes. It'll choke if you make it try.
if sys.platform == "win32":
    os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('proxy_encoder')

app.autodiscover_tasks(
    ['resolve_proxy_encoder.proxy_encoder.tasks']
)

if not os.getenv('BROKER_URL'):
    try:
        app.config_from_object(config['celery_settings'])
    except:
        raise Exception('Environment variables must be set or celery_settings present in YAML config')