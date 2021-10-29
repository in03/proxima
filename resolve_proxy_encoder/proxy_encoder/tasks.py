#!/usr/bin/env python

from __future__ import absolute_import

import os

import yaml

from ffmpy import FFmpeg, FFRuntimeError
from .celery import app
from .helpers import check_wsl, get_wsl_path

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.yml")) as file: 
    config = yaml.safe_load(file)

    proxy_settings = config['proxy_settings']

#####################################################################

@app.task(acks_late = True, track_started = True, prefetch_limit = 1)
def encode(job):
  
    expected_proxy_path = job['Expected Proxy Path']

    if check_wsl():
        expected_proxy_path = get_wsl_path(job['Expected Proxy Path'])
    
    # Create path for proxy first
    os.makedirs(
        expected_proxy_path, 
        exist_ok=True,
    )
    
    # Paths
    source_file = job['File Path']

    output_file = os.path.join(
        expected_proxy_path,
        os.path.splitext(job['Clip Name'])[0] +
        proxy_settings['ext'],
    )
    
    # Video
    h_res = proxy_settings['h_res']
    v_res = proxy_settings['v_res']
    fps = job['FPS']


    # Flip logic:
    # If any flip args were sent with the job from Resolve, flip the clip accordingly. 
    # Flipping should be applied to clip attributes, not through the inspector panel

    flippage = ''
    if job['H-FLIP'] == "On":
        flippage += ' hflip, '
    if job['V-FLIP'] == "On":
        flippage += 'vflip, '

    ff = FFmpeg(
        global_options = [
            '-y', 
            '-hide_banner', 
            '-stats', 
            '-loglevel error',
                         
        ],

        inputs = {source_file: None},
        outputs = {
            output_file:
                ['-c:v', 
                    'dnxhd', 
                    '-profile:v',
                    'dnxhr_sq', 
                    '-vf',
                    f'scale={h_res}:{v_res},{flippage}' + 
                    f'fps={fps},' + 
                    'format=yuv422p', 
                    '-c:a',
                    'pcm_s16le', 
                    '-ar', 
                    '48000',
                ]
        },
    )
    


    print(ff.cmd)
    try:
        ff.run()
    except FFRuntimeError as e:
        print(e)
        return ("FAILED encoding job: %s", 
                job['File Path'])
    else:
        return ("SUCCESS encoding job: %s", 
                job['File Path'])
