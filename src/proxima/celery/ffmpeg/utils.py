import json
import logging
import os
import shlex
import subprocess
from fractions import Fraction

from proxima.app import core

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")


def cleanup_working_dir(dir):
    """Cleanup temporary working directory"""

    if os.path.exists(dir):
        try:
            os.rmdir(dir)
        except Exception as e:
            print(f"Couldn't remove {dir}. In use?\n{e}")
            return False
    else:
        print(f"File: '{dir}' already deleted. No action taken.")

    return True


def frac_to_tc(frames, fps):
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


def frac_to_dec(fraction: str):
    """Convert a fraction to a decimal"""
    f = Fraction(fraction)
    return float(f)


def ffprobe(file) -> dict:
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
        raise ValueError("Couldn't get file metadata with ffprobe")

    return json_result
