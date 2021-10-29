
# Launch multiple workers

from enum import auto
import multiprocessing
import platform
import os
import subprocess
import time
import logging
import sys

from colorama import Fore, init
from pyfiglet import Figlet

# VARIABLES #
# windows_worker_cmd = """start /min py -m celery -A proxy_encoder worker -l INFO -E -P solo"""
# linux_worker_cmd = """xterm py -m celery -A proxy_encoder worker -l INFO -E -P solo"""

SEP = os.path.sep
APP_NAME = 'proxy_encoder'
start_worker_cmd = """start /min py -m celery -A proxy_encoder worker -l INFO -E -P solo"""


def filename_figlet():
    """Print the name of the script in big green letters"""
    script_name = os.path.basename(sys.argv[0])
    fig = Figlet()
    print(Fore.GREEN + fig.renderText(script_name))

def exit_in_seconds(timeout):
    '''Allow time to read console before exit'''
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
        print(f"{Fore.YELLOW}How many workers would you like to start?\n" +
              f"Press ENTER for default: {safe_cores_suggestion}\n")

        answer = int(input() or safe_cores_suggestion)

    except ValueError:
        invalid_answer()

    if answer == 0:
        print(f"{Fore.YELLOW}Using suggested amount: {safe_cores_suggestion}")
        answer = safe_cores_suggestion

    return answer

def launch_workers(workers_to_launch: int):

    # Start launching
    for i in range(0, workers_to_launch):

        dots = "."
        for x in range(0, i):
            dots = dots + "."

        # Add worker number to differentiate
        multi_worker_fmt = f" -n worker{i+1}@%h"
        launch_cmd = start_worker_cmd + multi_worker_fmt

        logging.info(launch_cmd)

        process = subprocess.Popen(
            launch_cmd, 
            shell = True,
        )

        sys.stdout.write(Fore.GREEN + f"\rLAUNCHING{dots}")
        sys.stdout.flush()
    return
    
def main():
    """ Main function """

    # Coloured term output
    init(autoreset = True)

    # Set loglevel
    logging.basicConfig(level=logging.WARNING)

    init()
    filename_figlet()
    os_ = platform.system()
    cpu_cores = multiprocessing.cpu_count()

    print(f"{Fore.GREEN}Running on {os_} with {cpu_cores} cores.\n")

    # Check OS isn't Linux
    if platform.system() == "Linux":
        print(f"{Fore.RED}This utility is for Windows only!\n" +
                "To start multiple workers on Linux or WSL, setup a systemd service.")
        sys.exit(1)

    print("For maximum performance, start as many workers as CPU cores.")
    print("Default recommendation is 2 cores spare for Resolve and other tasks.\n")

    launch_workers(prompt_worker_amount(cpu_cores))

    print(f"{Fore.GREEN}Done!")
    exit_in_seconds(5)

if __name__ == "__main__":
    main()

    