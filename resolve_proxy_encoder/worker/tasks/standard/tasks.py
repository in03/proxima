#!/usr/bin/env python3.6

from __future__ import absolute_import

import os

from ffmpy import FFmpeg, FFRuntimeError
from resolve_proxy_encoder.worker.celery import app
from resolve_proxy_encoder.worker.helpers import check_wsl, get_wsl_path
from resolve_proxy_encoder.settings import app_settings

config = app_settings.get_user_settings()

@app.task(

    name='resolve_proxy_encoder.worker.tasks.standard.encode',
    acks_late = True, 
    track_started = True, 
    prefetch_limit = 1
)
def encode_proxy(job):
    """ 
    Celery task to encode proxy media using parameters in job argument
    and user-defined settings
    """
  
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
        config['proxy_settings']['ext'],
    )
    
    # Video
    h_res = config['proxy_settings']['h_res']
    v_res = config['proxy_settings']['v_res']
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
        return (f"{job['File Path']} encoding FAILED")
    else:
        return (f"{job['File Path']} encoded successfully")
