import json
import os
import platform
import shlex
import subprocess
import sys
import time
from fractions import Fraction

from resolve_proxy_encoder.helpers import (
    app_exit,
    get_package_current_commit,
    get_rich_logger,
)
from resolve_proxy_encoder.settings.app_settings import Settings

settings = Settings()
config = settings.user_settings

logger = get_rich_logger(config["app"]["loglevel"])


def get_queue():
    git_full_sha = get_package_current_commit("resolve_proxy_encoder")

    if not git_full_sha:
        logger.error(
            "[red]Couldn't get local package commit SHA!\n"
            + "Necessary to prevent version mismatches between queuer and worker.[/]"
        )
        app_exit(1, -1)

    return git_full_sha[::8]


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


def cleanup_working_dir(dir):
    """Cleanup temporary working directory"""

    if os.path.exists(dir):
        try:
            os.rmdir(dir)
        except:
            print(f"Couldn't remove {dir}. In use?")
            return False
    else:
        print(f"File: '{dir}' already deleted. No action taken.")

    return True


def frames_to_timecode(frames, fps):
    """Convert frames to FFMPEG compatible timecode, with microseconds instead of frames"""
    return "{0:02d}:{1:02d}:{2:02d}.{3:01d}".format(
        int(frames / (3600 * fps)),
        int(frames / (60 * fps) % 60),
        int(frames / fps % 60),
        int(frames % fps),
    )


def intersperse(lst, item: str) -> list:
    """Intersperse every item in list with 'item'"""
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


def fraction_to_decimal(fraction: str):
    """Convert a fraction to a decimal"""
    f = Fraction(fraction)
    return float(f)


def get_media_info(file):
    """Get media info from file using ffprobe"""

    cmd = f'ffprobe -v quiet -print_format json -show_format -show_streams "{file}"'
    logger.debug(f"FFprobe command: {cmd}")

    ps = subprocess.Popen(
        shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    result = ps.communicate()[0]
    clean_result = result.decode().strip()
    json_result = json.loads(clean_result)

    if not json_result:
        print(f"Couldn't get data!")
        sys.exit(1)

    return json_result

    """ 
    Get a single attribute from a file with ffprobe.
    Ffprobe must be on path.
    """

    cmd = f'ffprobe -hide_banner -v error -show_entries format=nb_frames -of default=noprint_wrappers=1:nokey=1 "{file}"'
    ps = subprocess.Popen(
        shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    output = ps.communicate()[0]
    nb_frames = output.decode().strip()

    if not nb_frames:
        print(f"Couldn't get number of frames!")
        sys.exit(1)

    print(nb_frames)

    nb_frames = str_to_num(nb_frames)
    return nb_frames
