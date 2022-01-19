#!/usr/bin/env python3.6

# Launch multiple workers

import logging
import multiprocessing
import os
import platform
import subprocess
import sys
import time

from colorama import Fore, init
from resolve_proxy_encoder.helpers import get_rich_logger, install_rich_tracebacks
from resolve_proxy_encoder.settings.app_settings import Settings

install_rich_tracebacks()
settings = Settings()
config = settings.user_settings

logger = get_rich_logger(config["loglevel"])

# Make sure the module path in the command below is up to date!
START_WIN_WORKER = """celery -A resolve_proxy_encoder.worker worker -l INFO -P solo"""


def exit_in_seconds(timeout):
    """Allow time to read console before exit"""
    for i in range(timeout, -1, -1):
        time.sleep(1)
        sys.stdout.write(Fore.RED + f"\rExiting in {str(i)}")
    return


def prompt_worker_amount(cpu_cores: int):
    """Prompt the user for the amount of Celery workers they want to run.
    Start 2 less workers than amount of CPU cores by default."""

    answer = 0
    safe_cores_suggestion = cpu_cores - 2

    def invalid_answer():
        """Restart prompt if answer invalid"""
        print(f"{Fore.RED}Invalid number! Please enter a whole number.")
        prompt_worker_amount(cpu_cores)

    try:

        # Input doesn't like parsing colours
        print(
            f"{Fore.YELLOW}How many workers would you like to start?\n"
            + f"Press ENTER for default: {safe_cores_suggestion}\n"
        )

        answer = int(input() or safe_cores_suggestion)

    except ValueError:
        invalid_answer()

    if answer == 0:
        print(f"{Fore.YELLOW}Using suggested amount: {safe_cores_suggestion}")
        answer = safe_cores_suggestion

    return answer


def launch_workers(workers_to_launch: int):

    # Start launching
    print(Fore.GREEN + "LAUNCHING")
    for i in range(0, workers_to_launch):

        dots = "."
        for x in range(0, i):
            dots = dots + "."

        # Add worker number to differentiate
        multi_worker_fmt = f" -n worker{i+1}@%h"
        launch_cmd = START_WIN_WORKER + multi_worker_fmt

        # Start min or norm?
        if config["celery_settings"]["worker_start_minimized"]:
            launch_cmd = "start /min " + launch_cmd
        else:
            launch_cmd = "start " + launch_cmd

        logging.info(launch_cmd)

        process = subprocess.Popen(
            launch_cmd,
            shell=True,
        )

        if config["loglevel"] == "WARNING":

            sys.stdout.write(dots)

        sys.stdout.flush()

    print()
    return


def main(workers: int = 0):
    """Main function"""

    # Coloured term output
    init(autoreset=True)

    # Set loglevel
    logging.basicConfig(level=logging.WARNING)

    os_ = platform.system()
    cpu_cores = multiprocessing.cpu_count()

    print(f"{Fore.GREEN}Running on {os_} with {cpu_cores} cores.\n")

    # Check OS isn't Linux
    if platform.system() == "Linux":
        print(
            f"{Fore.RED}This utility is for Windows only!\n"
            + "To start multiple workers on Linux or WSL, setup a systemd service."
        )
        sys.exit(1)

    print("For maximum performance, start as many workers as CPU cores.")
    print("Default recommendation is 2 cores spare for Resolve and other tasks.\n")

    if workers:
        launch_workers(workers)
    else:
        launch_workers(prompt_worker_amount(cpu_cores))

    print(f"\n{Fore.GREEN}Done!")
    exit_in_seconds(5)


if __name__ == "__main__":

    # Change to the expected directory of START_WIN_WORKER
    module_path = os.path.dirname(os.path.abspath(__file__))
    package_path = os.path.dirname(module_path)
    os.chdir(package_path)
    main(0)
