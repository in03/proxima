import logging
import os
import platform
import subprocess
from pathlib import Path

from ..app.utils import core
from ..settings.manager import SettingsManager
from ..worker.ffmpeg.utils import ffprobe

core.install_rich_tracebacks()

settings = SettingsManager()

logger = logging.getLogger(__name__)
logger.setLevel(settings["worker"]["loglevel"])

# Paths


def check_wsl() -> bool:
    """Return True if Python is running in WSL"""

    if platform.system() == "Linux":
        return "Microsoft" in platform.uname().release

    return False


def get_wsl_path(windows_path: str):
    """Convert windows host paths to WSL paths if running WSL"""

    try:

        wsl_path = subprocess.run(
            ["wslpath", windows_path], stdout=subprocess.PIPE
        ).stdout.decode("utf-8")
        if not wsl_path or wsl_path == None:
            return windows_path

    except:
        return windows_path

    return wsl_path


# Video


def get_queue():

    """Get Celery queue name (routing key) from package git commit short SHA

    Allows constraining tasks and workers to exact same version and prevent breaking changes.

    """

    if settings["app"]["disable_version_constrain"]:

        logger.warning(
            "[yellow]Version constrain is disabled!\n"
            "You [bold]must[/] ensure routing and version compatibility yourself!"
        )

        return "celery"

    vc_key_file = Path(__file__).parent.parent.parent.joinpath("version_constraint_key")
    with open(vc_key_file) as file:
        return file.read()


def get_input_level(job):
    """
    Match Resolve's set data levels ("Auto", "Full" or "Video")

    Uses ffprobe to probe file for levels if Resolve data levels are set to Auto.
    """

    def probe_for_input_range(job):
        """
        Probe file with ffprobe for colour range
        and map to ffmpeg 'in_range' value ("full" or "limited")
        """

        input = job["file_path"]
        streams = ffprobe(file=input)["streams"]

        # Get first valid video stream
        video_info = None
        for stream in streams:
            if stream["codec_type"] == "video":
                if stream["avg_frame_rate"] != "0/0":
                    video_info = stream
        assert video_info != None

        color_data = {k: v for k, v in video_info.items() if "color" in k}
        assert "color_range" in video_info.keys()
        logger.debug(f"[magenta]Probed color data:\n{color_data}")

        switch = {
            "pc": "in_range=full",
            "tv": "in_range=limited",
        }
        return switch[video_info["color_range"]]

    switch = {
        "Auto": probe_for_input_range(job),
        "Full": "in_range=full",
        "Video": "in_range=limited",
    }

    return switch[job["data_level"]]


def get_flip(job):

    flip = str()

    if job["h_flip"]:
        flip += " hflip, "

    if job["v_flip"]:
        flip += "vflip, "

    return flip


def ensure_output_paths(job):
    """
    Ensure output folder is writable, get path.

    Args:
        job (list): Job object

    Returns:
        output_path (path string): Path of output proxy file

    """
    logger.debug(f"Output Dir: '{job['proxy_dir']}'")

    os.makedirs(
        job["proxy_dir"],
        exist_ok=True,
    )

    output_path = os.path.join(
        job["proxy_dir"],
        os.path.splitext(job["file_name"])[0] + job["proxy_settings"]["ext"],
    )
    return output_path


def ensure_logs_output_path(job, output_path):
    """
    Ensure log folder is writable, get path.

    Args:
        job (list): Job object
        output_path(string): Proxy file output path

    Returns:
        logfile_path (path string): Path of output log file

    """

    encode_log_dir = job["paths_settings"]["ffmpeg_logfile_path"]
    os.makedirs(encode_log_dir, exist_ok=True)

    return os.path.normpath(
        os.path.join(
            encode_log_dir, os.path.splitext(os.path.basename(output_path))[0] + ".txt"
        )
    )
