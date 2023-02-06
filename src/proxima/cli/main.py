import logging
import subprocess
from typing import Optional, List

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from proxima import version_constraint


# Init classes
cli_app = typer.Typer()
console = Console()


def write_override_key(value: str):
    version_constraint.key = value


hide_banner = typer.Option(
    default=False, help="Hide the title and build info on startup"
)

override_vc_key = typer.Option(
    default="",
    help="Override the version constraint key with a custom value",
    callback=write_override_key,
)

# Special functions


@cli_app.callback(invoke_without_command=True)
def run_without_args(ctx: typer.Context):
    sub = ctx.invoked_subcommand
    if sub is None:
        print("Run [bold]proxima --help[/] for a list of commands")
        # status()
    else:
        print(Panel(f"[bold]{sub.capitalize()}", expand=False))


# Commands
@cli_app.command()
def status():
    from proxima.app.checks import AppStatus

    app_status = AppStatus("proxima")
    print(app_status.status_panel)


@cli_app.command()
def queue(
    vc: str = override_vc_key,
):
    """
    Queue proxies from the currently open
    DaVinci Resolve timeline
    """

    # Init
    from proxima.settings import settings
    from proxima.app import core

    core.setup_rich_logging()
    logger = logging.getLogger("proxima")
    logger.setLevel(settings["app"]["loglevel"])

    print(version_constraint.key)

    from proxima.cli import queue

    queue.main(version_constraint.key)


@cli_app.command()
def work(
    hide_banner: bool = hide_banner,
    vc: str = override_vc_key,
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
            "[green bold]Starting workers![/] :construction_worker:", align="left"
        )
    else:
        console.rule(
            "[green bold]Starting worker launcher prompt[/] :construction_worker:",
            align="left",
        )

    print("\n")

    from proxima.celery import launch_workers

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
    console.rule("[red bold]Purge all tasks! :fire:", align="left")
    print("\n")

    from proxima.app import package
    from proxima.celery.celery import celery_queue

    subprocess.run(
        [
            package.get_script_from_package("celery"),
            "-A",
            "proxima.celery",
            "purge",
            "-Q",
            celery_queue,
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

    Runs `celery -A proxima.celery [celery_command]`
    at the absolute location of the package's Celery executable.
    Useful when the celery project is buried in a virtual environment and you want
    to do something a little more custom like purge jobs from a custom queue name.

    See https://docs.celeryq.dev/en/latest/reference/cli.html for proper usage.
    """

    print("\n")
    console.rule("[cyan bold]Celery command :memo:", align="left")
    print("\n")

    from proxima.app import package

    subprocess.run(
        [
            package.get_script_from_package("celery"),
            "-A",
            "proxima.celery",
            *celery_command,
        ]
    )


@cli_app.command()
def config():
    """Open user settings configuration file for editing"""
    from proxima.settings import settings

    print("\n")
    console.rule("[green bold]Open 'user_settings.yaml' config[/] :gear:", align="left")
    print("\n")

    typer.launch(settings.user_file)


def main():
    status()
    cli_app()


if __name__ == "__main__":
    main()
