""" Helper functions for main module """
from asyncio import subprocess

import json
import logging
import requests
import sys
import time
from typing import Union

import pkg_resources
import subprocess
from notifypy.notify import Notify

from rich.logging import RichHandler
from rich.prompt import Prompt

from resolve_proxy_encoder import python_get_resolve


def get_rich_logger(loglevel: Union[int, str]):

    """Set logger to rich, allowing for console markup."""

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=loglevel,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_extra_lines=1,
                markup=True,
            )
        ],
    )
    logger = logging.getLogger("rich")
    return logger


logger = get_rich_logger("WARNING")


def install_rich_tracebacks(show_locals=False):
    """Install rich tracebacks"""
    from rich.traceback import install

    install(show_locals=show_locals)


def app_exit(level: int = 0, timeout: int = -1, cleanup_funcs: list = None):

    """
    Exit function to allow time to
    read console output if necessary before exit.
    Specify negative timeout to prompt exit instead of timeout.
    Provide a list of functions to call on cleanup if necessary.
    """

    # Run any cleanup functions
    if cleanup_funcs:

        for x in cleanup_funcs:
            if x is not None:
                x()

    if timeout < 0:
        Prompt("Press [yellow]ENTER[/] to exit")

    else:

        for i in range(timeout, -1, -1):

            time.sleep(1)
            sys.stdout.write(f"\rExiting in " + str(i))

        # Erase last line
        sys.stdout.write("\x1b[1A")
        sys.stdout.write("\x1b[2K")

    sys.exit(level)


def notify(message: str, title: str = "Resolve Proxy Encoder"):
    """Cross platform system notification

    Args:
        message(str): Message to display
        title(str): Title of notification

    Returns:
        True/False(bool): Success/Failure

    Raises:
        none

    """

    logger = get_rich_logger("WARNING")

    try:

        notification = Notify()
        notification.title = title
        notification.message = message
        notification.send(block=False)

    except Exception as e:
        logger.exception(f"[red] :warning: Couldn't send notification.[/]\n{e}")
        return False

    return True


def get_resolve_objects():
    """Return necessary Resolve objects with error handling"""

    logger = get_rich_logger("WARNING")

    try:

        resolve = python_get_resolve.GetResolve()
        if resolve is None:
            raise TypeError

    except:

        logger.warning(
            "[red] :warning: Couldn't access the Resolve Python API. Is DaVinci Resolve running?[/]",
            extra={"markup": True},
        )
        app_exit(1, -1)

    try:

        project = resolve.GetProjectManager().GetCurrentProject()
        if project is None:
            raise TypeError

    except:

        logger.warning(
            "[red] :warning: Couldn't get current project. Is a project open in Resolve?[/]",
            extra={"markup": True},
        )
        app_exit(1, -1)

    try:

        timeline = project.GetCurrentTimeline()
        if timeline is None:
            raise TypeError
    except:

        logger.warning(
            "[red] :warning: Couldn't get current timeline. Is a timeline open in Resolve?[/]",
            extra={"markup": True},
        )
        app_exit(1, -1)

    try:

        media_pool = project.GetMediaPool()
        if media_pool is None:
            raise TypeError

    except:

        logger.warning(
            "[red] :warning: Couldn't get Resolve's media pool.[/]",
            extra={"markup": True},
        )
        app_exit(1, -1)

    return dict(
        resolve=resolve,
        project=project,
        timeline=timeline,
        media_pool=media_pool,
    )


def get_package_current_commit(package_name: str) -> Union[str, None]:
    """Attempt to find the current commit SHA from the locally installed package or the local GitHub repo.

    Args:
        - package_name (str): The name of the package to get last commit from.

    Returns:
        - latest_commit_id (str): The commit ID.
        - None: on fail

    Raises:
        - TypeError: Caught by try/except; used to jump between blocks, readability.
    """

    try:

        logger.info("Getting commit ID from package dist info.")

        dist = pkg_resources.get_distribution(package_name)
        vcs_metadata_file = dist.get_metadata("direct_url.json")
        vcs_metadata = json.loads(vcs_metadata_file)
        package_latest_commit = vcs_metadata["vcs_info"]["commit_id"]

        if package_latest_commit is None:
            raise TypeError("Couldn't get package last commit id")

        return package_latest_commit

    except:
        logger.info(
            "[yellow]Couldn't get package dist info, assuming git repo.[/]",
            extra={"markup": True},
        )

    try:
        logger.info("[cyan]Getting commit ID from git[/]")

        latest_commit_id = subprocess.check_output(
            'git --no-pager log -1 --format="%H"', stderr=subprocess.STDOUT, shell=True
        ).decode()

        if latest_commit_id is None:
            raise TypeError("Couldn't get git last commit id")

        return latest_commit_id

    except:

        logger.warning(
            f"[yellow]Couldn't get git info or package dist info!\n"
            + "Check properly cloned or installed[/]",
            extra={"markup": True},
        )
        return None


def get_remote_latest_commit(github_url: str) -> Union[str, None]:
    """Attempt to find the the origin GitHub repo's latest commit SHA for the main branch.

    This currently only works with GitHub!

    Args:
        - github_url (str): The URL of the origin repo.

    Returns:
        - remote_latest_commit (str): The latest commit's SHA.
        - None: on fail

    Raises:
        - TypeError: Caught by try/except; used to jump between blocks, readability.
    """

    url_list = github_url.split(".com")[1].split("/")
    api_endpoint = (
        f"https://api.github.com/repos/{url_list[1]}/{url_list[2]}/commits/main"
    )

    try:

        r = requests.get(api_endpoint, timeout=5)
        if r.status_code != 200:
            logger.warning(f"[yellow]Couldn't fetch commits from GitHub API:\n{r}[/]")
            return None
    # TODO: catch the timeout exception properly
    except ConnectTimeoutError:
        logger.error("[red]Couldn't connect to GitHub.[/]")

    results = r.json()
    remote_latest_commit = results["sha"]
    return remote_latest_commit


def check_for_updates(github_url: str, package_name: str) -> Union[str, None]:
    """Compare git origin to local git or package dist for updates

    Args:
        - github_url(str): origin repo url
        - package_name(str): offical package name

    Returns:
        - none

    Raises:
        - none
    """

    logger.info("[cyan]Checking for updates...[/]")
    remote_latest_commit = get_remote_latest_commit(github_url)
    package_latest_commit = get_package_current_commit(package_name)

    if not remote_latest_commit or not package_latest_commit:
        logger.warning("[red]Failed to check for updates[/]")

    if remote_latest_commit != package_latest_commit:

        logger.warning(
            "[yellow]Update available.\n"
            + "Fully uninstall and reinstall when possible:[/]\n"
            + '"pip uninstall resolve-proxy-encoder"\n'
            + f'"pip install git+{github_url}"\n'
        )

        logger.info(f"Remote: {remote_latest_commit}")
        logger.info(f"Current: {package_latest_commit}")

    else:
        logger.info("[green]Installation up-to-date[/]")

    return
