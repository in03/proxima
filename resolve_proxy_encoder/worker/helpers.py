import platform
import subprocess

from resolve_proxy_encoder.helpers import (
    app_exit,
    get_package_current_commit,
    get_rich_logger,
)

from resolve_proxy_encoder.settings.app_settings import Settings


settings = Settings()
config = settings.user_settings

logger = get_rich_logger(config["app"]["loglevel"])


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

    # Add git SHA Celery queue to prevent queuer/worker incompatibilities
    git_full_sha = get_package_current_commit("resolve_proxy_encoder")

    if config["app"]["disable_version_constrain"]:
        logger.warning(
            "[yellow]Version constrain is disabled! Thar be dragons :dragon_face:[/]"
        )
        return "celery"

    if not git_full_sha:

        logger.error(
            "[red]Couldn't get local package commit SHA!\n"
            + "Necessary to maintain version constrain.[/]"
        )
        app_exit(1, -1)

    # TODO: `git_sha` slice returns as 5 characters, not standard 7
    # labels: bug

    # Use git standard 7 character short SHA
    return git_full_sha[::8]
