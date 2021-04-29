from __future__ import absolute_import

import os
import time

import yaml

from .celery import app

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.yml")) as file: 
    config = yaml.safe_load(file)


#####################################################################

def simulate_encode(job):
    '''Just something simple to simulate a quick encode job'''

    print(f"Started encoding {job.get('Clip Name', None)}")
    time.sleep(2)
    with open(os.path.join(script_dir, "render_log.txt"), "a") as file:
            file.write(f"Rendered:\n{job}")


@app.task
def encode_video(job):
    simulate_encode(job)
    return True