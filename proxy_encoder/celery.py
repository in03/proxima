from __future__ import absolute_import
from celery import Celery

import os
import yaml

script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.yml")) as file: 
    config = yaml.safe_load(file)

# Broker Settings
broker = config['rabbit_mq']
user = broker['user']
pwd = broker['password']
address = broker['address']
vhost = broker['vhost']
protocol = broker['protocol']
backend = broker['backend']

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('proxy_encoder',
             broker=f'{protocol}://{user}:{pwd}@{address}/{vhost}',
             backend=backend,
             include=['proxy_encoder.tasks'])