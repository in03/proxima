#!/usr/bin/env python3.6

from __future__ import absolute_import

import os

from better_ffmpeg_progress import FfmpegProcess
from pymediainfo import MediaInfo
from resolve_proxy_encoder import helpers
from resolve_proxy_encoder.helpers import (
    get_rich_logger,
    install_rich_tracebacks,
    app_exit,
)
from resolve_proxy_encoder.settings.app_settings import Settings
from resolve_proxy_encoder.worker.celery import app
from resolve_proxy_encoder.worker.helpers import check_wsl, get_wsl_path

settings = Settings()
config = settings.user_settings
logger = get_rich_logger(config["celery_settings"]["worker_loglevel"])
install_rich_tracebacks()

git_full_sha = helpers.get_package_current_commit("resolve_proxy_encoder")
if not git_full_sha:
    logger.error(
        "[red]Couldn't get local package commit SHA!\n"
        + "Necessary to prevent version mismatches between queuer and worker.[/]"
    )
    app_exit(1, -1)

git_short_sha = git_full_sha[::8]


@app.task(
    acks_late=True,
    track_started=True,
    prefetch_limit=1,
    soft_time_limit=60,
    queue=git_short_sha,
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

    def get_timecode(job):
        """Get timecode using MediaInfo"""

        file_path = job["File Path"]
        media_info = MediaInfo.parse(file_path)

        data_track_exists = False
        for track in media_info.tracks:

            if track.track_type == "Other":

                data_track_exists = True
                if track.time_code_of_first_frame:

                    logger.info("Using embedded timecode.")
                    return str(track.time_code_of_first_frame)

        if data_track_exists:
            logger.warning("Couldn't get timecode from media's data track.")
        else:
            logger.info(
                "No embedded timecode found in media file. Using default timecode."
            )
        return "00:00:00:00"

    ffmpeg_command = [
        "ffmpeg",
        "-y",  # Never prompt!
        *misc_args,  # User global settings
        "-i",
        source_file,
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
        "-timecode",
        get_timecode(job),
        output_file,
    ]

    logger.info(f"FFmpeg command:\n{' '.join(ffmpeg_command)}")

    # NOT-TODO: Fix terminal progress output on newline
    # Currently BetterFFMpegProgress is logging progress increments to newlines.
    # It's better than nothing, but it looks awful. There are other issues with BFP too.
    # Logging to files is messy, etc. Maybe steal the FFMpeg progress parsing func and
    # use rich.progress instead.
    # labels: bug

    process = FfmpegProcess(
        command=[*ffmpeg_command], ffmpeg_loglevel=proxy_settings["ffmpeg_loglevel"]
    )

    # Per-file encode log location
    encode_log_dir = os.path.join(
        os.path.dirname(output_file),
        "encoding_logs",
    )

    # Make logs subfolder
    os.makedirs(encode_log_dir, exist_ok=True)
    encode_log_file = os.path.join(
        encode_log_dir, os.path.splitext(os.path.basename(output_file))[0] + ".txt"
    )

    # Run encode job
    try:
        process.run(ffmpeg_output_file=encode_log_file)

    except Exception as e:
        logger.exception(f"[red] :warning: Couldn't encode proxy.[/]\n{e}")

    return f"{source_file} encoded successfully"
