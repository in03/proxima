import logging
import platform
import subprocess
from pathlib import Path

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
            "You [bold]must[/] ensure routing and version compatibility yourself!"
        )

        return "celery"

    vc_key_file = Path(__file__).parent.parent.parent.joinpath("version_constraint_key")
    with open(vc_key_file) as file:
        return file.read()
