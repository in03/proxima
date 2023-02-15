import logging
import os
import shutil
import subprocess
from typing import List, Optional

import typer
from pyfiglet import Figlet
from rich import print
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax

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


def get_proxima_env_vars():
    prefix: str = "PROXIMA"
    variables: dict[str, str] = {}

    for key, value in os.environ.items():
        if key.startswith(prefix):
            variables.update({key: value})
    return variables


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


@config_app.callback(
    invoke_without_command=True,
    help="Run `config` without args or options to validate and print configuration",
)
def config_callback(ctx: typer.Context):
    if ctx.invoked_subcommand:
        return
    from proxima.settings.manager import settings

    if settings:
        print(settings.dict())


# TODO: Big flaw. Python environment vars are not system env vars.
# We technically want to interface with system environment variables.
# Settings vars here only affects child processes, not current or parent
# How naughty is it to actually change system environment variables?
# Frowned upon? Maybe should re-evalate if we should provide
# the facility for CRUD or just Read.


@config_app.command("env")
def manage_env(
    view: bool = typer.Option(
        False, "--view", help="Print the current toml configuration to stdout"
    ),
    set: Optional[str] = typer.Argument(
        None, show_default=False, help="Set an environment variable."
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Reset .env configuration to app defaults.",
        show_default=False,
    ),
    force: bool = typer.Option(
        False, "--force", help="Bypass any confirmation prompts.", show_default=False
    ),
):
    """
    Manage .env configuration

    Environment variables override toml configuration.

    This allows for easy unit testing and quick changes
    in different deployment environments.

    See docs for a list of usable environment variables.
    """

    # Print current user config to stdout
    if view:
        [print(f"{x}={os.environ[x]}") for x in get_proxima_env_vars()]
        return

    # Launch editor
    if set:
        # TODO: Validate environment variable belongs to Proxima
        try:
            key, val = set.split("=")
            key = key.upper()
            key = "PROXIMA__" + key.replace(".", "__")
            key = key.strip()
            val = val.strip()

            os.environ[key] = val
            print(f"Set environment variable: '{key}'")

        except ValueError as e:
            print(e)
        return

    # Reset .env file to empty
    if reset:
        # Prompt for confirmation if not forced
        if not force:
            if not Confirm.ask(
                "[yellow]Woah! The action you're about to perform is un-undoable![/]\n"
                "Are you sure you want to reset the toml configuration file to defaults?"
            ):
                return

        for var in get_proxima_env_vars().keys():
            os.environ[var] = ""
            logger.debug(f"[magenta]Unset environment var {var}")
        return

    # Fallback to default: print current user config to stdout
    [print(f"{x}={os.environ[x]}") for x in get_proxima_env_vars()]


@config_app.command("dotenv")
def manage_dotenv(
    view: bool = typer.Option(
        False, "--view", help="Print the current toml configuration to stdout"
    ),
    edit: bool = typer.Option(
        False, "--edit", help="Edit the .env configuration file.", show_default=False
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Reset .env configuration to app defaults.",
        show_default=False,
    ),
    force: bool = typer.Option(
        False, "--force", help="Bypass any confirmation prompts.", show_default=False
    ),
):
    """
    Manage .env configuration

    Environment variables override toml configuration.

    This allows for easy unit testing and quick changes
    in different deployment environments.

    See docs for a list of usable environment variables.
    """

    from proxima.settings import dotenv_settings_file

    # Ensure exists
    if not os.path.exists(dotenv_settings_file):
        with open(dotenv_settings_file, "x"):
            print("[cyan]Initialised .env config file")

    # Print current user config to stdout
    if view:
        print(
            Syntax.from_path(
                dotenv_settings_file, theme="nord-darker", line_numbers=True
            )
        )

    # Launch editor
    if edit:
        print("[cyan]Editing .env config file")
        typer.launch(str(dotenv_settings_file))
        return

    # Reset .env file to empty
    if reset:
        # Prompt for confirmation if not forced
        if not force:
            if not Confirm.ask(
                "[yellow]Woah! The action you're about to perform is un-undoable![/]\n"
                "Are you sure you want to reset the toml configuration file to defaults?"
            ):
                return

        with open(dotenv_settings_file, "w"):
            print("[cyan]Reset toml config file to defaults")
        return

    # Fallback to default: print current user config to stdout
    print(
        Syntax.from_path(dotenv_settings_file, theme="nord-darker", line_numbers=True)
    )


@config_app.command("toml")
def manage_toml(
    view: bool = typer.Option(
        False, "--view", help="Print the current toml configuration to stdout"
    ),
    edit: bool = typer.Option(
        False, "--edit", help="Edit the toml configuration file.", show_default=False
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Reset toml configuration to app defaults.",
        show_default=False,
    ),
    force: bool = typer.Option(
        False, "--force", help="Bypass any confirmation prompts.", show_default=False
    ),
):
    """
    Manage toml configuration

    Toml holds all configuration by default.

    Toml configuration can be changed, reset to defaults,

    as well as overriden by environment variables set in shell or .env.
    """

    from proxima.settings import default_settings_file, user_settings_file

    # Ensure exists
    if not os.path.exists(user_settings_file):
        with open(user_settings_file, "x"):
            print("[cyan]Initialised user toml config file")

    # Print current user config to stdout
    if view:
        print(
            Syntax.from_path(user_settings_file, theme="nord-darker", line_numbers=True)
        )

    # Launch editor
    if edit:
        print("[cyan]Editing user toml config file")
        typer.launch(str(user_settings_file))

    # Reset .toml file to defaults
    if reset:
        # Prompt for confirmation if not forced
        if not force:
            if not Confirm.ask(
                "[yellow]Woah! The action you're about to perform is un-undoable![/]\n"
                "Are you sure you want to reset the toml configuration file to defaults?"
            ):
                shutil.move(default_settings_file, user_settings_file)
                print("[cyan]Reset toml config to defaults")
                return

    # Fallback to default: print current user config to stdout
    print(Syntax.from_path(user_settings_file, theme="nord-darker", line_numbers=True))


@config_app.command("reset")
def reset_all_configuration(
    force: bool = typer.Option(
        False, "--force", help="Bypass any confirmation prompts.", show_default=False
    )
):
    """
    Completely reset user configuration to defaults.

    This will result in '.env' being made empty,
    local environment variables being unset,
    and 'user_settings.toml' being reset to default values.
    USE WITH CAUTION!
    """

    # Prompt for confirmation if not forced
    if not force:
        if not Confirm.ask(
            "[yellow]Woah! The action you're about to perform is un-undoable![/]\n"
            "Are you sure you want to reset all user configuration to defaults?"
        ):
            return

    manage_env(edit=False, reset=True, force=True)
    manage_dotenv(edit=False, reset=True, force=True)
    manage_toml(edit=False, reset=True, force=True)


def main():
    fig = Figlet(font="rectangles")
    print(fig.renderText("proxima"))
    cli_app()


if __name__ == "__main__":
    main()
