""" Helper functions for main module """

import logging
import sys
import time
from typing import Union

from rich.logging import RichHandler
from rich.prompt import Prompt
from win10toast import ToastNotifier

from .settings import app_settings

config = app_settings.get_user_settings()

def get_rich_logger(loglevel:Union[int, str]="WARNING"):


    """ Set logger to rich, allowing for console markup."""

    FORMAT = "%(message)s"
    logging.basicConfig(

        level = loglevel, 
        format = FORMAT, 
        datefmt = "[%X]", 
        handlers = [

            RichHandler(
                rich_tracebacks = True,
                tracebacks_extra_lines = 1,
                markup = True,
            )
        ],
    )
    logger = logging.getLogger("rich")
    return logger

def app_exit(level:int=0, timeout:int=5, cleanup_funcs:list=None):

    """ 
    Exit function to allow time to 
    read console output if necessary before exit.
    Specify negative timeout to prompt exit instead of timeout.
    Provide a list of functions to call on cleanup if necessary.
    """

    logger = get_rich_logger(config['loglevel'])

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
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')

    sys.exit(level)

def toast(message, threaded = True):
    toaster = ToastNotifier()
    toaster.show_toast(
        "Queue Proxies", 
        message, 
        # icon_path = icon_path, 
        threaded = threaded,
    )
    return
