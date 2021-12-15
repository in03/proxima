#!/usr/bin/env python3.6

from __future__ import absolute_import

import os

from ffmpy import FFmpeg, FFRuntimeError
from resolve_proxy_encoder.helpers import get_rich_logger, install_rich_tracebacks
from resolve_proxy_encoder.settings import app_settings
from resolve_proxy_encoder.worker.celery import app
from resolve_proxy_encoder.worker.helpers import check_wsl, get_wsl_path

config = app_settings.get_user_settings()
logger = get_rich_logger(config["celery_settings"]["worker_loglevel"])
# install_rich_tracebacks()


@app.task(
    acks_late=True,
    track_started=True,
    prefetch_limit=1,
    soft_time_limit=60,
)
def encode_proxy(job):
    """
    Celery task to encode proxy media using parameters in job argument
    and user-defined settings
    """

    # Variables
    try:

        proxy_settings = config["proxy_settings"]

        # Get required job metadata
        clip_name = job["Clip Name"]
        source_file = job["File Path"]
        expected_proxy_dir = job["Expected Proxy Dir"]

        # Get proxy settings
        vid_codec = proxy_settings["vid_codec"]
        vid_profile = proxy_settings["vid_profile"]
        pix_fmt = proxy_settings["pix_fmt"]
        h_res = proxy_settings["h_res"]
        v_res = proxy_settings["v_res"]
        proxy_ext = proxy_settings["ext"]
        audio_codec = proxy_settings["audio_codec"]
        audio_samplerate = proxy_settings["audio_samplerate"]
        misc_args = proxy_settings["misc_args"]

    except KeyError as e:

        logger.error(f"Job missing required key: {e}")
        raise e

    if check_wsl():
        expected_proxy_dir = get_wsl_path(expected_proxy_dir)

    # Create path for proxy first
    try:

        os.makedirs(
            expected_proxy_dir,
            exist_ok=True,
        )

    except OSError as e:
        logger.error(f"Error creating proxy directory: {e}")
        raise e

    output_file = os.path.join(
        expected_proxy_dir,
        os.path.splitext(clip_name)[0] + proxy_ext,
    )

    def get_orientation(job):
        """Get the video orientation from job metadata in FFmpeg syntax

        Some footage is shot upside-down. If we flip the clip from Resolve's clip attributes,
        we need to make sure we flip the proxy as well. Unforunately flipping proxies isn't applied
        in realtime as needed, so proxies will need to be rerendered if orientation changes.

        Args:
            job (dict): Resolve job metadata

        Returns:
            flip_logic (str): FFmpeg syntax for video orientation

        Raises:
            KeyError: If the job metadata doesn't contain the necessary orientation keys

        """
        try:

            flip = str()

            if job["H-FLIP"] == "On":
                flip += " hflip, "

            if job["V-FLIP"] == "On":
                flip += "vflip, "

        except KeyError as e:
            logger.error("Couldn't get video orientation from job metadata!")
            raise e

        return flip

    ff = FFmpeg(
        global_options=[
            "-y",  # Never prompt!
            *misc_args,  # User global settings
        ],
        inputs={source_file: None},
        outputs={
            output_file: [
                "-c:v",
                vid_codec,
                "-profile:v",
                vid_profile,
                "-vsync",
                "-1",  # Necessary to match VFR
                "-vf",
                f"scale={h_res}:{v_res},{get_orientation(job)}" f"format={pix_fmt}",
                "-c:a",
                audio_codec,
                "-ar",
                audio_samplerate,
                "-copyts",  # Timecode MUST match source
            ]
        },
    )
    logger.info(ff.cmd)

    try:

        ff.run()

    except Exception as e:
        raise Exception(f"[red] :warning: Couldn't encode proxy.[/]\n{e}")

    return f"{source_file} encoded successfully"
