
# Launch multiple workers

import multiprocessing
import platform
import os
import time
import logging
import sys
from subprocess import Popen

from colorama import Fore, init
from pyfiglet import Figlet

# VARIABLES #
windows_worker_cmd = """start /min py -m celery -A proxy_encoder worker -l INFO -E -P eventlet --concurrency=1"""
linux_worker_cmd = """xterm py -m celery -A proxy_encoder worker -l INFO -E --concurrency=1"""

# Set loglevel
logging.basicConfig(level=logging.WARNING)

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

    
    safe_cores_suggestion = cpu_cores - 2

    def invalid_answer():
        """Restart prompt if answer invalid"""
        print(Fore.RED + "Invalid number! Please enter a whole number.")
        prompt_worker_amount()

    try:

        answer = int(
            input(
                Fore.YELLOW + "How many workers would you like to start?" +
                f" DEFAULT: {safe_cores_suggestion}\n"
            ) or 
            safe_cores_suggestion
        )

    except ValueError:
        invalid_answer()

    if answer is 0:
        print(Fore.YELLOW + "Using suggested amount: %s", safe_cores_suggestion)
        answer = safe_cores_suggestion

    return answer

def launch_workers(os_: str, workers_to_launch: int):

    # Get Launch CMD
    if os_ is "Windows":
        platform_cmd = windows_worker_cmd
    elif os_ is "Linux":
        platform_cmd = linux_worker_cmd
    else:
        print(Fore.RED + "Aborting! Unsupported worker OS: %s", os_)
        sys.exit(1)

    # Start launching
    for i in range(0, workers_to_launch):

        dots = "."
        for x in range(0, i):
            dots = dots + "."

        # Add worker number to differentiate
        multi_worker_fmt = f" -n worker{i+1}@%h"
        launch_cmd = platform_cmd + multi_worker_fmt

        logging.info(launch_cmd)

        process = Popen(
            launch_cmd, 
            shell = True,
        )

        sys.stdout.write(Fore.GREEN + f"\rLAUNCHING{dots}")
        sys.stdout.flush()
    return

if __name__ == "__main__":

    # Coloured term output
    init(
        autoreset = True, 
        convert = True
    )

    filename_figlet()

    os_ = platform.system()
    cpu_cores = multiprocessing.cpu_count()
    
    print("\n" + Fore.YELLOW + f"This computer has {cpu_cores} cores.\n")
    print("For maximum performance, start as many workers as CPU cores.")
    print("Default recommendation is 2 cores spare for Resolve and other tasks.\n")

    workers_to_launch = prompt_worker_amount(cpu_cores)

    launch_workers(os_, workers_to_launch)

    print(Fore.GREEN + "Done!")
    exit_in_seconds(5)

    
