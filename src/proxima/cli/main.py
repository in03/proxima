import logging
import os
import shutil
import subprocess
from enum import Enum
from typing import List, Literal, Optional

import typer
from pyfiglet import Figlet
from rich import print
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax

from proxima.settings import (
    default_settings_file,
    dotenv_settings_file,
    user_settings_file,
)

# Init classes
cli_app = typer.Typer()
config_app = typer.Typer()
cli_app.add_typer(config_app, name="config")

console = Console()

logger = logging.getLogger("proxima")


def write_override_key(value: str):
    if value:
        logger.warning(f"[yellow]Version constraint key overriden with '{value}'")
        os.environ["PROXIMA_VC_KEY"] = value


# Special functions


@cli_app.callback(invoke_without_command=True)
def global_options(
    ctx: typer.Context,
    vc=typer.Option(
        default="",
        help="Override the version constraint key with a custom value",
        callback=write_override_key,
    ),
):
    print(
        "\nDistributed transcoding for DaVinci Resolve proxies!\n"
        "https://in03.github.io/proxima\n"
    )

    sub = ctx.invoked_subcommand
    if sub is None:
        print("Run [bold]proxima --help[/] for a list of commands")


# Commands


@cli_app.command()
def status():
    from proxima.app.checks import AppStatus

    app_status = AppStatus("proxima")
    print(app_status.status_panel)


@cli_app.command()
def queue():
    """
    Queue proxies from the currently open
    DaVinci Resolve timeline
    """

    # Init
    from proxima.app import core
    from proxima.settings.manager import settings

    core.setup_rich_logging()
    logger = logging.getLogger("proxima")
    logger.setLevel(settings.dict()["app"]["loglevel"])

    from proxima.cli import queue

    queue.main()


@cli_app.command()
def work(
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

    subprocess.run(
        [
            package.get_script_from_package("celery"),
            "-A",
            "proxima.celery",
            "purge",
            "-Q",
            str(os.getenv("PROXIMA_VC_KEY")),
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


@config_app.callback(invoke_without_command=True)
def config_callback(ctx: typer.Context):
    """
    Manage Proxima's configuration

    Proxima's configuration is layered.

    Toml is populated with modifiable defaults.

    .env overrides toml configuration.
    Environment variables override .env and toml.

    Run `--help` on any of the below commands for further details.
    """

    # Ensure 'user_settings_file' exists
    if not os.path.exists(user_settings_file):
        with open(user_settings_file, "x"):
            print("[cyan]Initialised user toml config file")

    # Ensure 'dotenv_settings_file' exists
    if not os.path.exists(dotenv_settings_file):
        with open(dotenv_settings_file, "x"):
            print("[cyan]Initialised dotenv config file")

    if ctx.invoked_subcommand:
        return
    from proxima.settings.manager import settings

    if settings:
        print("[[magenta]Consolidated configuration]")
        print(settings.dict())


class RWConfigTypes(str, Enum):
    """Read and writable config types"""

    dotenv = "dotenv"
    toml = "toml"


class RConfigTypes(str, Enum):
    """Readable config types"""

    env = "env"
    dotenv = "dotenv"
    toml = "toml"


@config_app.command("view")
def view_configuration(
    config_type: RConfigTypes = typer.Argument(
        ..., help="View configuration", show_default=False
    )
):
    """
    Print the current user configuration to screen.

    Supply a configuration type to view, or run
    `proxima config` to see consolidated configuration.
    """

    match config_type:
        case "dotenv":
            print("[[magenta]Proxima dotenv configuration]")
            print(
                Syntax.from_path(
                    dotenv_settings_file, theme="nord-darker", line_numbers=True
                )
            )

        case "env":
            print("[[magenta]Proxima environment variables]")

            prefix: str = "PROXIMA"
            variables: dict[str, str] = {}
            for key, value in os.environ.items():
                if key.startswith(prefix):
                    variables.update({key: value})

            [print(f"{x}={os.environ[x]}") for x in variables]
            return

        case "toml":
            print("[[magenta]Proxima toml configuration]")
            print(
                Syntax.from_path(
                    user_settings_file, theme="nord-darker", line_numbers=True
                )
            )

        case _:
            raise typer.BadParameter(f"Unsupported config type: '{config_type}'")


@config_app.command("edit")
def edit_configuration(
    config_type: RWConfigTypes = typer.Argument(
        ..., help="Edit configuration", show_default=False
    )
):
    """
    Edit provided user configuration.

    Note that environment variables, while supported,
    are not editable here.

    Modify them in your own shell environment.
    """

    match config_type:
        case "dotenv":
            print("[cyan]Editing .env config file")
            typer.launch(str(dotenv_settings_file))
            return

        case "toml":
            print("[cyan]Editing user toml config file")
            typer.launch(str(user_settings_file))

        case _:
            raise typer.BadParameter(f"Unsupported config type: '{config_type}'")


@config_app.command("reset")
def reset_configuration(
    config_type: RWConfigTypes = typer.Argument(
        ..., help="Reset configuration", show_default=False
    ),
    force: bool = typer.Option(
        False, "--force", help="Bypass any confirmation prompts.", show_default=False
    ),
):
    """
    Reset the provided user configuration type.

    Be aware that this is IRREVERSIBLE.
    """

    if not force:
        if not Confirm.ask(
            "[yellow]Woah! The action you're about to perform is un-undoable![/]\n"
            f"Are you sure you want to reset the {config_type} configuration file to defaults?"
        ):
            return

    match config_type:
        case "dotenv":
            with open(dotenv_settings_file, "w"):
                print("[cyan]Reset toml config file to defaults")
                return

        case "toml":
            shutil.move(default_settings_file, user_settings_file)
            print("[cyan]Reset toml config to defaults")
            return


@config_app.command("reset")
def reset_all_configuration(
    force: bool = typer.Option(
        False, "--force", help="Bypass any confirmation prompts.", show_default=False
    )
):
    """
    Reset ALL user configuration types to defaults.

    This will result in '.env' being made empty
    and 'user_settings.toml' being reset to default values.

    Environment variables will NOT be unset.
    Run `proxima view env` to see their current values.
    """

    # Prompt for confirmation if not forced
    if not force:
        if not Confirm.ask(
            "[yellow]Woah! The action you're about to perform is un-undoable![/]\n"
            "Are you sure you want to reset all user configuration to defaults?"
        ):
            return

    reset_configuration(config_type=RWConfigTypes.dotenv, force=True)
    reset_configuration(config_type=RWConfigTypes.toml, force=True)


def main():
    fig = Figlet(font="rectangles")
    print(fig.renderText("proxima"))
    cli_app()


if __name__ == "__main__":
    main()
