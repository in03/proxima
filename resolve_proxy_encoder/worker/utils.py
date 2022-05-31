import logging
import platform
import subprocess

from ..app.utils import core, pkg_info
from ..settings.manager import SettingsManager

core.install_rich_tracebacks()

settings = SettingsManager()

logger = logging.getLogger(__name__)
logger.setLevel(settings["worker"]["loglevel"])


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


def get_queue():

    """Get Celery queue name (routing key) from package git commit short SHA

    Allows constraining tasks and workers to exact same version and prevent breaking changes.

    """

    if settings["app"]["disable_version_constrain"]:

        logger.warning(
            "[yellow]Version constrain is disabled!\n"
            "You [bold]must[/] ensure routing and version compatability yourself!"
        )

        return "celery"

    # NOTE: Can't get short-sha from version-info from settings since it's never persisted to disk
    # and the workers are spawned as new processes! Must get package commit afresh.
    pkg_commit = pkg_info.get_package_current_commit("resolve_proxy_encoder")
    return pkg_commit[-4:] if pkg_commit else None
