import platform
import subprocess

from resolve_proxy_encoder.utils.general import (
    app_exit,
    get_package_current_commit,
    get_rich_logger,
)
from resolve_proxy_encoder.settings.manager import SettingsManager

config = SettingsManager()

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
