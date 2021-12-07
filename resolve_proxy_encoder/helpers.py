""" Helper functions for main module """
import json
import logging
import requests
import sys
import time
from typing import Union

import pkg_resources
import semver
from rich.logging import RichHandler
from rich.prompt import Prompt
from win10toast import ToastNotifier

from resolve_proxy_encoder import python_get_resolve
from resolve_proxy_encoder.settings import app_settings

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

def get_resolve_objects():
    """ Return necessary Resolve objects with error handling"""

    logger = get_rich_logger()

    try:

        resolve = python_get_resolve.GetResolve()

    except:

        logger.warning("[red] :warning: Couldn't access the Resolve Python API. Is DaVinci Resolve running?[/]", 
            extra = {"markup":True}
        )
        app_exit(1, -1)

    try:

        project = resolve.GetProjectManager().GetCurrentProject()

    except:

        logger.warning(
            "[red] :warning: Couldn't get current project. Is a project open in Resolve?[/]",
            extra = {"markup":True}
        )
        app_exit(1, -1)

    try:

        timeline = project.GetCurrentTimeline()

    except:

        logger.warning(
            "[red] :warning: Couldn't get current timeline. Is a timeline open in Resolve?[/]",
            extra = {"markup":True}
        )
        app_exit(1, -1)

    try:

        media_pool = project.GetMediaPool()

    except:

        logger.warning(
            "[red] :warning: Couldn't get Resolve's media pool.[/]",
            extra = {"markup":True}
        )
        app_exit(1, -1)
        

    return dict(
        resolve = resolve, 
        project = project,
        timeline = timeline,
        media_pool = media_pool,
    )

def get_package_last_commit(package_name):
    """ Get the ID of the last VCS commit pushed when this package was installed.
    
    Uses `direct_url.json` from the site-package's `dist-info`.

    Args:
        package_name (str): The name of the package to get last commit from.

    Returns:
        package_last_commit_id (str): The commit ID.
        None

    Raises:
        none: 
    """

    dist = pkg_resources.get_distribution(package_name)

    try:

        vcs_metadata_file = dist.get_metadata("direct_url.json")
        vcs_metadata = json.loads(vcs_metadata_file)
        package_last_commit_id = vcs_metadata['vcs_info']['commit_id']

    except KeyError:
        print("Couldn't get commit_id from 'direct_url.json'")

    return package_last_commit_id

def get_remote_last_commit(github_url):

    owner, sep, repo_name = github_url.split(".com")[1].split("/")
    api_endpoint = f"https://api.github.com/repos{owner}/{repo_name}/commits"
    headers = {'content-type': 'application/json'}

    print(api_endpoint)

    results = requests.get(api_endpoint)
    print(results)
    return results

# def get_package_semver(package_name):
#     """ Get and parse a package's semver if exists.

#     Args:
#         package_name (str): the name of the package
    
#     Returns:
#     """

#     dist = pkg_resources.get_distribution(package_name)
#     semver.VersionInfo.parse(dist)