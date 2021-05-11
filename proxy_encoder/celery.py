#!/usr/bin/env python

from __future__ import absolute_import
from celery import Celery

import os
import yaml

script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.yml")) as file: 
    config = yaml.safe_load(file)

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('proxy_encoder')
app.config_from_object('proxy_encoder.celery_settings')
