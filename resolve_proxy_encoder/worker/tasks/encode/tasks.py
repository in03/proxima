#!/usr/bin/env python3.6

import logging
import os
from webbrowser import get

from ....app.utils import core
from ....settings.manager import SettingsManager
from ....worker.celery import app
from ....worker.ffmpeg.ffmpeg_process import FfmpegProcess
from ....worker.utils import check_wsl, get_wsl_path, get_queue

from rich import print
from rich.console import Console

# Worker and Celery settings pulled from local user_settings file
# All other settings are passed from queuer
settings = SettingsManager()
console = Console()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["worker"]["loglevel"])


@app.task(
    bind=True,
    acks_late=True,
    track_started=True,
    prefetch_limit=1,
    soft_time_limit=60,
    queue=get_queue(),
)
def encode_proxy(self, job):

    """
    Celery task to encode proxy media using parameters in job argument
    and user-defined settings
    """

    # Use app configuration passed in task
    proxy_settings = job["proxy_settings"]
    path_settings = job["paths_settings"]

    print("\n")
    console.rule(f"[green]Received proxy encode job :clapper:[/]", align="left")
    print("\n")

    logger.info(
        f"[magenta bold]Job: [/]{self.request.id}\n" f"Input File: '{job['file_path']}'"
    )

    # TODO: Integrate cross-platform path mapping. Move `check_wsl` func.
    # Convert paths for WSL
    if check_wsl():
        job["proxy_dir"].update(get_wsl_path(job["proxy_dir"]))

    # Create proxy dir

    logger.debug(f"Output Dir: '{job['proxy_dir']}'")
    try:

        os.makedirs(
            job["proxy_dir"],
            exist_ok=True,
        )

    except OSError as e:
        logger.error(f"Error creating proxy directory: {e}")
        raise e

    output_file = os.path.join(
        job["proxy_dir"],
        os.path.splitext(job["file_name"])[0] + proxy_settings["ext"],
    )
    logger.info(f"Output File: '{output_file}'\n")

    # Get Resolutions
    source_res = [int(x) for x in job["resolution"]]
    v_res = int(proxy_settings["vertical_res"])
    logger.info(f"Source Resolution: {source_res}")

    def get_flip():

        flip = str()
        logger.info(
            f"Horizontal Flip: {job['h_flip']}\n" f"Vertical Flip: {job['h_flip']}"
        )

        if job["h_flip"]:
            flip += " hflip, "

        if job["v_flip"]:
            flip += "vflip, "

        return flip

    # Log Timecode
    logger.info(f"Starting Timecode: {job['start_tc']}")

    # Get FFmpeg Command
    ffmpeg_command = [
        "ffmpeg",
        "-y",  # Never prompt!
        *proxy_settings["misc_args"],  # User global settings
        "-i",
        job["file_path"],
        "-c:v",
        proxy_settings["codec"],
        "-profile:v",
        proxy_settings["profile"],
        "-vsync",
        "-1",  # Necessary to match VFR
        "-vf",
        f"scale=-2:{v_res},{get_flip()} format={proxy_settings['pix_fmt']}",
        "-c:a",
        proxy_settings["audio_codec"],
        "-ar",
        proxy_settings["audio_samplerate"],
        "-timecode",
        job["start_tc"],
        output_file,
    ]

    print()  # Newline
    logger.debug(f"[magenta]Running! FFmpeg command:[/]\n{' '.join(ffmpeg_command)}\n")

    process = FfmpegProcess(
        command=[*ffmpeg_command], ffmpeg_loglevel=proxy_settings["ffmpeg_loglevel"]
    )

    # Make logs subfolder
    encode_log_dir = path_settings["ffmpeg_logfile_path"]
    os.makedirs(encode_log_dir, exist_ok=True)

    encode_log_file = os.path.normpath(
        os.path.join(
            encode_log_dir, os.path.splitext(os.path.basename(output_file))[0] + ".txt"
        )
    )

    logger.debug(f"[magenta]Encoder logfile path: {encode_log_file}[/]")

    # Run encode job
    logger.info("[yellow]Encoding...[/]")

    try:
        process.run(logfile=encode_log_file)

    except Exception as e:
        logger.exception(f"[red] :warning: Couldn't encode proxy.[/]\n{e}")

    return f"{job['file_name']} encoded successfully"
