#!/usr/bin/env python

from __future__ import absolute_import

import os
import time

import yaml

from ffmpy import FFmpeg, FFRuntimeError
from .celery import app

# Get environment variables #########################################
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.yml")) as file: 
    config = yaml.safe_load(file)

    proxy_settings = config['proxy_settings']

#####################################################################

def simulate_encode(job):
    '''Just something simple to simulate a quick encode job'''

    print(f"Started encoding {job.get('Clip Name', None)}")
    time.sleep(2)
    with open(os.path.join(script_dir, "render_log.txt"), "a") as file:
            file.write(f"\n\nRendered:\n{job}")


    # C:\Program Files\FFMPEG\ffmpeg.exe" -y -i "B:/Yeet.mp4" -c:v dnxhd -profile:v dnxhr_sq -vf scale=1280:720,fps=50.000,format=yuv422p -c:a pcm_s16le -ar 48000 -hide_banner -stats -loglevel error "B:/Sup.mp4"
    # ffmpeg -y -hide-banner -stats -loglevel error -i B:/Yeet.mp4 -c:v dnxhd -profile:v dnxhr_s1 -vf scale=1280:720 fps=50 format=yuv422p "-c:a pcm_s16le" "-ar 48000" B:/Sup.mp4

@app.task(acks_late = True, track_started = True, prefetch_limit = 1)
def encode(job):
    
    # Create path for proxy first
    os.makedirs(
        job['Expected Proxy Path'], 
        exist_ok=True,
    )
    
    # Paths
    source_file = job['File Path']

    output_file = os.path.join(
        job['Expected Proxy Path'],
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
        return False
    else:
        return job
