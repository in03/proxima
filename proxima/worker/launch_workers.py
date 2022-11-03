# Launch multiple workers

import logging
import multiprocessing
import os
import platform
import subprocess
import shortuuid
import time
from shutil import which

from rich import print

from proxima.app import core
from proxima.app.utils import package
from proxima.settings import settings
from proxima.app.celery import get_version_constraint_key, get_queue

core.install_rich_tracebacks()

logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


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


def new_worker(nickname: str = "") -> int:
    """
    Start a new celery worker in a new process

    Used to start workers even when the script binaries are buried
    in a virtual env like in pipx.

    Args:
        nickname (str, optional): Used to differentiate multiple workers on the same host.
        Defaults to None.

    Returns:
        int: Process ID of the new subprocess (pid)
    """

    def get_worker_name(nickname):

        # @h for 'hostname'
        return f"-n {nickname}@{platform.node()}"

    def get_worker_queue():

        return f" -Q {get_version_constraint_key()},all"

    def get_new_console():
        """Get os command to spawn process in a new console window"""

        # Get new terminal
        worker_terminal_args = settings["worker"]["terminal_args"]

        # Check if any args are on path. Probably terminal executable.
        executable_args = [which(x) for x in worker_terminal_args]
        if executable_args:
            return ""

        # TODO: Ensure partial matches work here too
        # Make sure no starting args exist
        start_commands = ["open", "start"]
        if any(x in start_commands for x in worker_terminal_args):
            return ""

        # TODO: Need to test starting workers on other platforms
        # Get new terminal cmd
        os_ = platform.system()

        if os_ == "Windows":
            return 'start "Proxima worker"'  # First double quotes as title

        elif os_ == "Mac":
            return "open"

        elif os_ == "Linux":
            logger.error(
                "Cannot guess installed Linux terminal. Too many distros."
                + "Please provide a terminal executable in 'worker_terminal_args' settings."
            )
            core.app_exit(1, -1)
        else:
            logger.error(
                f"Could not determine terminal executable for OS: {os_}."
                + "Please provide a terminal executable in 'worker_terminal_args' settings."
            )
            core.app_exit(1, -1)

    launch_cmd = [
        get_new_console(),
        *settings["worker"]["terminal_args"],
        f'"{package.get_script_from_package("celery")}"',
        "-A proxima.worker",
        "worker",
        get_worker_name(nickname),
        get_worker_queue(),
        *settings["worker"]["celery_args"],
    ]

    logger.info(f"[cyan]NEW WORKER - {nickname}[/]")
    logger.debug(f"[magenta]{' '.join(launch_cmd)}[/]\n")

    process = subprocess.Popen(
        # TODO: This was causing the worker start cmd to fail after changing to absolute imports
        # Not sure why we needed it in the first place? Would be good to do further testing and see
        # if it is necessary in some cases.
        # labels: testing
        # cwd=get_module_path(),
        args=" ".join(launch_cmd),
        shell=True,
    )
    return process.pid


def launch_workers(workers_to_launch: int) -> list[str]:

    # Start launching

    pids = []
    for _ in range(0, workers_to_launch):
        pids.append(new_worker(nickname=shortuuid.uuid()[:5]))
        time.sleep(0.3)
    return pids


def main(workers: int = 0):
    """Main function"""

    os_ = platform.system()
    cpu_cores = multiprocessing.cpu_count()

    queue_name = get_queue()
    if not queue_name:
        raise TypeError("Couldn't get queue!")

    print()
    logger.info(f"[cyan]Consuming from queue with key: '{queue_name}'\n")

    # Don't bother with tips if not prompting
    if workers:

        launch_workers(workers)

    else:

        print(f"[green]Running on {os_} with {cpu_cores} cores.[/]\n")
        print("For maximum performance, start as many workers as CPU cores.")
        print("Default recommendation is 2 cores spare for Resolve and other tasks.\n")
        launch_workers(prompt_worker_amount(cpu_cores))

    print(f"[green]Done![/]")
    core.app_exit(0, 2)


if __name__ == "__main__":

    # Change to the expected directory of START_WIN_WORKER
    module_path = os.path.dirname(os.path.abspath(__file__))
    package_path = os.path.dirname(module_path)

    os.chdir(package_path)
    main(0)
