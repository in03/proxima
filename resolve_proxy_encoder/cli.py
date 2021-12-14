#!/usr/bin/env python3.6


import subprocess
import webbrowser

import typer
from pyfiglet import Figlet
from rich import print
from rich.prompt import Confirm

from resolve_proxy_encoder.helpers import get_rich_logger
from resolve_proxy_encoder.settings import app_settings

# Print CLI title
fig = Figlet()
text = fig.renderText("Resolve Proxy Encoder")
print(f"[green]{text}[/]")

config = app_settings.get_user_settings()
logger = get_rich_logger(config["loglevel"])
app = typer.Typer()

# default_loglevel = app_settings.get_defaults()["loglevel"]
# if config.get("loglevel") != default_loglevel:
#     print(f"Custom loglevel set:[/]'{config.get('loglevel')}'\n")


@app.command()
def queue():
    """
    Queue proxies from the currently open
    DaVinci Resolve timeline
    """
    print("[green]Queuing proxies from Resolve's active timeline[/] :outbox_tray:")

    from resolve_proxy_encoder import resolve_queue_proxies

    resolve_queue_proxies.main()


@app.command()
def link():
    """
    Manually link proxies from directory to
    source media in open DaVinci Resolve project
    """

    from resolve_proxy_encoder import link_proxies

    link_proxies.main()


@app.command()
def work(number: int = 0):
    """Prompt to start Celery workers on local machine"""
    if number > 0:
        print(f"[green]Starting workers! :construction_worker:[/]")
    print(f"[cyan]Starting worker launcher prompt :construction_worker:[/]")

    from resolve_proxy_encoder import start_workers

    start_workers.main(number)


@app.command()
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

    if Confirm.ask(
        "[yellow]Are you sure you want to purge all tasks?\n"
        "All active tasks and task history will be lost![/]"
    ):
        print("[green]Purging all worker queues[/] :fire:")
        subprocess.run(["celery", "-A", "resolve_proxy_encoder.worker", "purge", "-f"])


@app.command()
def mon():
    """
    Launch Flower Celery monitor in default browser new window
    """

    print("[green]Launching Flower celery monitor[/] :sunflower:")
    webbrowser.open_new(config["celery_settings"]["flower_url"])


def main():
    app()


if __name__ == "__main__":
    main()
