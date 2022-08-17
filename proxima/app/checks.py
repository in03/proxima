import logging
import pathlib
import time
from typing import Union

from rich import print
from rich.prompt import Confirm
from yaspin import yaspin

from .utils import pkg_info

from ..app.utils import core
from ..settings.manager import SettingsManager
from ..worker.celery import app as celery_app

settings = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)


def check_for_updates(github_url: str, package_name: str) -> Union[dict, None]:

    """Compare git origin to local git or package dist for updates

    Args:
        - github_url(str): origin repo url
        - package_name(str): offical package name

    Returns:
        - dict:
            - 'is_latest': bool,
            - 'current_version': git_short_sha

    Raises:
        - none
    """

    latest = False

    spinner = yaspin(
        text="Checking for updates...",
        color="cyan",
    )
    spinner.start()

    build_info = pkg_info.get_build_info(package_name)
    if build_info["build"] != "git":

        spinner.fail("❌ ")
        logger.warning(
            "[yellow][bold]WIP:[/bold] Currently unable to check for release updates[/]"
        )
        return None

    if not build_info["version"]:

        spinner.fail("❌ ")
        logger.warning("[yellow]Unable to retrieve package version[/]")
        return None

    if not settings["app"]["check_for_updates"]:

        return {
            "is_latest": None,
            "remote_commit": None,
            "package_commit": build_info["version"],
            "commit_short_sha": build_info["version"][:7:],
        }

    remote_commit = pkg_info.get_remote_current_commit(github_url)

    if not remote_commit or not build_info["version"]:

        spinner.fail("❌ ")
        logger.warning("[red]Failed to check for updates[/]")
        return None

    elif remote_commit != build_info["version"]:

        spinner.ok("🔼 ")
        logger.warning(
            "[yellow]Update available.\n"
            + "Fully uninstall and reinstall when possible:[/]\n"
            + '"pip uninstall resolve-proxima"\n'
            + f'"pip install git+{github_url}"\n'
        )

        logger.debug(f"Remote: {remote_commit}")
        logger.debug(f"Current: {build_info['version']}")

    else:

        latest = True
        spinner.ok("✨ ")

    return {
        "is_latest": latest,
        "remote_commit": remote_commit,
        "package_commit": build_info["version"],
        "commit_short_sha": build_info["version"][:7:],
    }


def check_worker_compatibility():

    online_workers = celery_app.control.inspect().active_queues()
    logger.debug(f"[magenta]Online workers:[/]\n{online_workers}")

    if settings["app"]["disable_version_constrain"]:
        logger.warning(
            "[yellow]Version constrain is disabled![/] [red][bold]Thar be dragons :dragon_face:\n"
        )
        time.sleep(2)
        return

    spinner = yaspin(
        text="Checking worker compatibility...",
        color="cyan",
    )

    # Get online workers
    if online_workers is None:

        spinner.fail("❌ ")
        logger.warning(
            "[yellow]No workers found. Can't check compatibility.\n"
            + "Jobs may not be received if no compatible workers are available!\n[/]"
            + "[red]CONTINUE AT OWN RISK![/]\n"
        )

        if not Confirm.ask(
            "[yellow]No workers found.[/] [cyan]Do you wish to continue?[/]"
        ):
            core.app_exit(1, -1)

        return

    # Get current version constraint key
    spinner.start()

    try:
        vc_key_file = pathlib.Path(__file__).parent.parent.parent.joinpath(
            "version_constraint_key"
        )
        with open(vc_key_file) as file:
            queuer_vc_key = file.read()

        if not queuer_vc_key:
            raise ValueError("VC key file is empty!")

    except ValueError and FileNotFoundError as error:

        spinner.fail("❌ ")
        logger.warning(
            "[yellow]Couldn't get version constraint key from file.\n"
            "Any incompatible workers will not be reported.\n"
            "[red]CONTINUE AT OWN RISK![/]\n"
            f"[red]{error}[/]"
        )
        return None

    # Get incompatible workers
    incompatible_workers = []
    compatible_workers = []
    for worker, attributes in online_workers.items():

        worker_vc_key = attributes[0]["routing_key"]

        worker_dict = {
            "name": worker,
            "host": str(worker).split("@")[1],
            "version_constraint_key": worker_vc_key,
        }

        # Compare git sha
        if not worker_vc_key == queuer_vc_key:
            incompatible_workers.append(worker_dict)
        else:
            compatible_workers.append(worker_dict)

    incompatible_hosts = set()
    for x in incompatible_workers:
        incompatible_hosts.add(x["host"])

    compatible_hosts = set()
    for x in compatible_workers:
        compatible_hosts.add(x["host"])

    # Prompt incompatible workers
    if incompatible_workers:
        spinner.fail("❌ ")

        # Get singular or plural based on list lengths
        worker_plural = "workers" if len(online_workers) > 1 else "worker"
        incompatible_hosts_count = len(incompatible_hosts)
        multi_incompatible_hosts_warning = (
            f"across {len(incompatible_hosts)} hosts "
            if incompatible_hosts_count > 1
            else ""
        )

        logger.warning(
            f"[yellow]Incompatible {worker_plural} detected!\n"
            + f"{len(incompatible_workers)}/{len(online_workers)} workers {multi_incompatible_hosts_warning}are incompatible.\n"
            + f"Only compatible workers can consume jobs from this queuer.[/]\n"
            + f"\nTo fix, update any incompatible hosts to match this build's version constraint key.\n"
            + f"\n[magenta]Incompatible hosts:\n{incompatible_hosts}[/]"
            + "\n"
        )

        # If no compatible workers are available
        if len(online_workers) == len(incompatible_workers):

            spinner.fail("❌ ")
            logger.error(
                "[red]All online workers are incompatible!\n" + "Cannot continue[/]"
            )
            core.app_exit(1, -1)

        else:

            if not Confirm.ask("[cyan]Do you wish to continue?[/]"):
                core.app_exit(1, -1)

    spinner.ok("👍 ")
    return
