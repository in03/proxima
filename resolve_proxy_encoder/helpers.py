""" Helper functions for main module """

import logging
import sys
import time
from typing import Union

from resolve_proxy_encoder import python_get_resolve
from resolve_proxy_encoder.settings import app_settings
from rich.logging import RichHandler
from rich.prompt import Prompt
from win10toast import ToastNotifier

config = app_settings.get_user_settings()


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


def app_exit(level: int = 0, timeout: int = 5, cleanup_funcs: list = None):

    """
    Exit function to allow time to
    read console output if necessary before exit.
    Specify negative timeout to prompt exit instead of timeout.
    Provide a list of functions to call on cleanup if necessary.
    """

    logger = get_rich_logger(config["loglevel"])

    # Run any cleanup functions
    if cleanup_funcs:

        logger.debug(f"Running cleanup funcs: {cleanup_funcs}")

        for x in cleanup_funcs:

            if x is not None:

                logger.debug(f"Running: {x}")
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


def toast(message, threaded=True):
    toaster = ToastNotifier()
    toaster.show_toast(
        "Queue Proxies",
        message,
        # icon_path = icon_path,
        threaded=threaded,
    )
    return


def get_resolve_objects():
    """Return necessary Resolve objects with error handling"""

    logger = get_rich_logger(config["loglevel"])

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
