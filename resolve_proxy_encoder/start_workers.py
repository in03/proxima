#!/usr/bin/env python3.6

# Launch multiple workers

import multiprocessing
import os
import platform
import re
import subprocess
import sys
import time
from distutils.sysconfig import get_python_lib
from pathlib import Path
from shutil import which

from rich import print
from rich.progress import Progress

from resolve_proxy_encoder.helpers import (
    app_exit,
    get_package_current_commit,
    get_rich_logger,
    get_script_from_package,
    install_rich_tracebacks,
)
from resolve_proxy_encoder.settings.app_settings import Settings
from resolve_proxy_encoder.worker.celery import app

install_rich_tracebacks()
settings = Settings()
config = settings.user_settings
logger = get_rich_logger(loglevel=config["celery_settings"]["worker_loglevel"])

# TODO: 'rprox work' command is incompatible with pipx!
# Because we call our worker from celery as a subprocess we need to either call it
# programmatically somehow or create a "rprox start worker" command that takes celery args,
# but wraps the first part of the cmd.
# labels: bug, critical


def prompt_worker_amount(cpu_cores: int):
    """Prompt the user for the amount of Celery workers they want to run.
    Start 2 less workers than amount of CPU cores by default."""

    answer = 0
    safe_cores_suggestion = cpu_cores - 2

    def invalid_answer():
        """Restart prompt if answer invalid"""
        print(f"[red]Invalid number! Please enter a whole number.[/]")
        prompt_worker_amount(cpu_cores)

    try:

        # Input doesn't like parsing colours
        print(
            f"[yellow]How many workers would you like to start?[/]\n"
            + f"Press ENTER for default: {safe_cores_suggestion}\n"
        )

        answer = int(input() or safe_cores_suggestion)

    except ValueError:
        invalid_answer()

    if answer == 0:
        print(f"[yellow]Using suggested amount: {safe_cores_suggestion}[/]")
        answer = safe_cores_suggestion

    return answer


def get_routing_key_from_version():

    # Add git SHA Celery queue to prevent queuer/worker incompatibilities
    git_full_sha = get_package_current_commit("resolve_proxy_encoder")

    if not git_full_sha:

        logger.error(
            "[red]Couldn't get local package commit SHA!\n"
            + "Necessary to prevent version mismatches between queuer and worker.[/]"
        )
        app_exit(1, -1)

    # Use git standard 7 character short SHA
    return git_full_sha[::8]


def new_worker(id=None):
    """Start a new celery worker in a new process

    Used to start workers even when the script binaries are buried
    in a virtual env like in pipx.

    Args:
        - id: Used to differentiate multiple workers on the same host

    Returns:
        - none

    Raises:
        - none
    """

    # Get worker name
    worker_name = []

    if id:
        worker_name = [
            "-n",
            f"worker{id}",
            "@h",  # hostname
        ]

    # Get worker queue
    routing_key = get_routing_key_from_version()
    queue = [" -Q " + routing_key]

    # TODO: Test that celery binary can be started from pipx install

    # Get celery binary
    if which("celery"):

        celery_bin = "celery"

    else:

        # Celery bin not on path. Maybe virtual env. Find.
        site_packages_dir = Path(get_python_lib()).resolve()
        celery_bin = get_script_from_package("Celery")
        print(celery_bin)
        package_root = os.path.join(site_packages_dir, "resolve_proxy_encoder")

        # Change dir to package root
        os.chdir(package_root)

    launch_cmd = [
        *config["celery_settings"]["worker_terminal_args"],
        celery_bin,
        "-A",
        "resolve_proxy_encoder.worker",
        "worker",
        *worker_name,
        *queue,
        *config["celery_settings"]["worker_celery_args"],
    ]

    # TODO: Figure out why celery worker is failing to start
    # "Error: Unable to parse extra configuration from command line."
    # Not sure why, copying the cmd and pasting runs the worker fine...
    # labels: bug

    logger.info(launch_cmd)
    print(launch_cmd)
    process = subprocess.Popen(launch_cmd)


def launch_workers(workers_to_launch: int):

    # Start launching

    worker_id = 0
    with Progress() as progress:

        launch = progress.add_task(
            "[green]Starting workers[/]", total=workers_to_launch
        )

        while not progress.finished:

            worker_id += 1
            progress.update(launch, advance=1)

            # logger.info(launch_cmd)

            new_worker(id=worker_id)
            time.sleep(0.05)

        print()
        return


def main(workers: int = 0):
    """Main function"""

    os_ = platform.system()
    cpu_cores = multiprocessing.cpu_count()

    print(f"[green]Running on {os_} with {cpu_cores} cores.[/]\n")

    # Check OS isn't Linux
    if not platform.system() == "Windows":
        print(
            f"[red]This utility is for Windows only!\n"
            + "To start multiple workers on Linux or WSL, setup a systemd service."
        )
        sys.exit(1)

    print("For maximum performance, start as many workers as CPU cores.")
    print("Default recommendation is 2 cores spare for Resolve and other tasks.\n")

    if workers:
        launch_workers(workers)
    else:
        launch_workers(prompt_worker_amount(cpu_cores))

    print(f"[green]Done![/]")
    app_exit(0, 5)


if __name__ == "__main__":

    # Change to the expected directory of START_WIN_WORKER
    module_path = os.path.dirname(os.path.abspath(__file__))
    package_path = os.path.dirname(module_path)
    os.chdir(package_path)
    main(0)
