#!/usr/bin/env python3.6

import logging
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from merge_args import merge_args
from pyfiglet import Figlet
from rich import print
from rich.console import Console
from rich.prompt import Confirm
from rich.rule import Rule

from .utils import pkg_info

# Init classes
cli_app = typer.Typer()
console = Console()

# TODO: Add global option to hide banner
# labels: enhancement
hide_banner = typer.Option(
    default=False, help="Hide the title and build info on startup"
)

# Special functions


@cli_app.callback(invoke_without_command=True)
def draw_banner():

    # Print CLI title
    fig = Figlet()
    text = fig.renderText("Resolve Proxy Encoder")
    print(f"[green]{text}\n")

    # Get build info
    build_info = pkg_info.get_build_info("Resolve-Proxy-Encoder")

    # Get VC key
    vc_key_file = Path(__file__).parent.parent.parent.joinpath("version_constraint_key")
    with open(vc_key_file) as file:
        vc_key = file.read()

    # Print banner data
    if build_info["build"] == "release":

        print(
            f"[bold]{str(build_info['build']).capitalize()} build[/] "
            f"{build_info['version']} | "
            f"[bold]VC key:[/] '{vc_key}'"
        )

    else:

        print(
            f"[bold]{str(build_info['build']).capitalize()} build[/] "
            f"{'([green]installed[/] :package:)' if build_info['installed'] else '([yellow]cloned[/] :hammer_and_wrench:)'} "
            f"'{build_info['version'][:7:]}' | "
            f"[bold]Version constraint key[/] '{vc_key}'"
        )

    Rule()


def run_checks():
    """Run before CLI App load."""

    from ..app import checks
    from ..settings.manager import SettingsManager

    settings = SettingsManager()

    # Check for any updates and inject version info into user settings.
    version_info = checks.check_for_updates(
        github_url=settings["app"]["update_check_url"],
        package_name="resolve_proxy_encoder",
    )

    settings.update({"version_info": version_info})


def cli_init():

    draw_banner()
    run_checks()


# Commands


@cli_app.command()
def queue():
    """
    Queue proxies from the currently open
    DaVinci Resolve timeline
    """

    # Init
    from ..app import checks
    from ..settings.manager import SettingsManager
    from .utils.core import setup_rich_logging

    settings = SettingsManager()

    setup_rich_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(settings["app"]["loglevel"])
    # End init

    checks.check_worker_compatibility()

    print("\n")
    console.rule(
        f"[green bold]Queuing proxies from Resolve's active timeline[/] :outbox_tray:",
        align="left",
    )
    print("\n")

    from ..queuer import queue

    queue.main()


@cli_app.command()
def link():
    """
    Manually link proxies from directory to
    source media in open DaVinci Resolve project
    """

    # Init
    from ..settings.manager import SettingsManager
    from .utils.core import setup_rich_logging

    settings = SettingsManager()

    setup_rich_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(settings["app"]["loglevel"])
    # End init

    from ..queuer import link

    print("\n")
    console.rule(f"[green bold]Link proxies[/] :link:", align="left")
    print("\n")

    link.main()


@cli_app.command()
def work(
    hide_banner: bool = hide_banner,
    workers_to_launch: Optional[int] = typer.Argument(
        0, help="How many workers to start"
    ),
):
    """Prompt to start Celery workers on local machine"""

    if not workers_to_launch:
        workers_to_launch = 0

    print("\n")

    if workers_to_launch > 0:
        console.rule(
            f"[green bold]Starting workers![/] :construction_worker:", align="left"
        )
    else:
        console.rule(
            f"[green bold]Starting worker launcher prompt[/] :construction_worker:",
            align="left",
        )

    print("\n")

    from ..worker import launch_workers

    launch_workers.main(workers_to_launch)


@cli_app.command()
def purge():
    """Purge all tasks from Celery.

    All tasks will be removed from all queues,
    including results and any history in Flower.

    Args:
        None
    Returns:
        None
    Raises:
        None
    """

    print("\n")
    console.rule(f"[red bold]Purge all tasks! :fire:", align="left")
    print("\n")

    if Confirm.ask(
        "[yellow]Are you sure you want to purge all tasks?\n"
        "All active tasks and task history will be lost![/]"
    ):
        print("[green]Purging all worker queues[/] :fire:")
        subprocess.run(["celery", "-A", "resolve_proxy_encoder.worker", "purge", "-f"])


@cli_app.command()
def mon():
    """
    Launch Flower Celery monitor in default browser new window
    """

    # Init
    from ..settings.manager import SettingsManager

    settings = SettingsManager()
    # End init

    print("\n")
    console.rule(
        f"[green bold]Start Flower Celery monitor[/] :sunflower:", align="left"
    )
    print("\n")

    webbrowser.open_new(settings["celery"]["flower_url"])


@cli_app.command()
def config():
    """Open user settings configuration file for editing"""

    from ..settings.manager import SettingsManager

    settings = SettingsManager()

    print("\n")
    console.rule(
        f"[green bold]Open 'user_settings.yaml' config[/] :gear:", align="left"
    )
    print("\n")

    webbrowser.open_new(settings.user_file)


# Other


def main():
    cli_app()


if __name__ == "__main__":
    main()
