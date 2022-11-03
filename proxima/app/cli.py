#!/usr/bin/env python3.6

import logging
import subprocess
from typing import Optional, List

import typer
from rich import print
from rich.console import Console


from proxima.settings import settings
from proxima.app.checks import AppStatus
from proxima.app.celery import get_version_constraint_key

# Init classes
cli_app = typer.Typer()
console = Console()
app_status = AppStatus("proxima")

hide_banner = typer.Option(
    default=False, help="Hide the title and build info on startup"
)

# Special functions
@cli_app.callback(invoke_without_command=True)
def run_without_args():
    # print("Run [bold]proxima --help[/] for a list of commands")
    ...


def cli_init():
    print(app_status.banner)


# Commands
@cli_app.command()
def status():
    print(app_status.status_panel)


@cli_app.command()
def queue():
    """
    Queue proxies from the currently open
    DaVinci Resolve timeline
    """

    # Init
    from proxima.app import core

    core.setup_rich_logging()
    logger = logging.getLogger(__name__)
    logger.setLevel(settings["app"]["loglevel"])
    # End init

    # print("\n")
    # console.rule(
    #     f"[green bold]Queuing proxies from Resolve's active timeline[/] :outbox_tray:",
    #     align="left",
    # )
    # print("\n")

    from proxima.queuer import queue

    queue.main()


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

    from proxima.worker import launch_workers

    launch_workers.main(workers_to_launch)


@cli_app.command()
def purge():
    """Purge all tasks from Celery according to VC key

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

    from proxima.app.utils import package

    subprocess.run(
        [
            package.get_script_from_package("celery"),
            "-A",
            "proxima.worker",
            "purge",
            "-Q",
            get_version_constraint_key(),
        ]
    )


@cli_app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def celery(
    ctx: typer.Context,
    celery_command: List[str] = typer.Argument(..., help="A command to pass to Celery"),
):
    """
    Pass commands to Celery buried in venv.

    Runs `celery -A proxima.worker [celery_command]`
    at the absolute location of the package's Celery executable.
    Useful when the celery project is buried in a virtual environment and you want
    to do something a little more custom like purge jobs from a custom queue name.

    See https://docs.celeryq.dev/en/latest/reference/cli.html for proper usage.
    """

    # print(ctx.params["celery_command"])

    print("\n")
    console.rule(f"[cyan bold]Celery command :memo:", align="left")
    print("\n")

    from proxima.app.utils import package

    subprocess.run(
        [
            package.get_script_from_package("celery"),
            "-A",
            "proxima.worker",
            *celery_command,
        ]
    )


@cli_app.command()
def config():
    """Open user settings configuration file for editing"""

    print("\n")
    console.rule(
        f"[green bold]Open 'user_settings.yaml' config[/] :gear:", align="left"
    )
    print("\n")

    typer.launch(settings.user_file)


def main():
    cli_init()
    cli_app()


if __name__ == "__main__":
    main()
