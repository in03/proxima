#!/usr/bin/env python3.6

import subprocess
import webbrowser

import typer
from pyfiglet import Figlet
from rich import print
from rich.prompt import Confirm

from resolve_proxy_encoder.worker.celery import app as celery_app
from resolve_proxy_encoder.helpers import check_for_updates, get_rich_logger
from resolve_proxy_encoder.settings.app_settings import Settings

# Print CLI title
fig = Figlet()
text = fig.renderText("Resolve Proxy Encoder")
print(f"[green]{text}[/]")

settings = Settings()
config = settings.user_settings

logger = get_rich_logger(config["loglevel"])

# Check for package / git updates
check_for_updates(
    github_url="https://github.com/in03/resolve-proxy-encoder",
    package_name="resolve_proxy_encoder",
)
print()


def check_worker_compatability():
    workers = celery_app.control.inspect().active_queues()
    worker_names = {k: v for k, v in workers.items()}
    print(worker_names)
    # celery_app.control.broadcast()
    return


check_worker_compatability()
cli_app = typer.Typer()


@cli_app.command()
def queue():
    """
    Queue proxies from the currently open
    DaVinci Resolve timeline
    """
    print("[green]Queuing proxies from Resolve's active timeline[/] :outbox_tray:")

    from resolve_proxy_encoder import resolve_queue_proxies

    resolve_queue_proxies.main()


@cli_app.command()
def link():
    """
    Manually link proxies from directory to
    source media in open DaVinci Resolve project
    """

    from resolve_proxy_encoder import link_proxies

    link_proxies.main()


@cli_app.command()
def work(number: int = 0):
    """Prompt to start Celery workers on local machine"""
    if number > 0:
        print(f"[green]Starting workers! :construction_worker:[/]")
    print(f"[cyan]Starting worker launcher prompt :construction_worker:[/]")

    from resolve_proxy_encoder import start_workers

    start_workers.main(number)


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

    print("[green]Launching Flower celery monitor[/] :sunflower:")
    webbrowser.open_new(config["celery_settings"]["flower_url"])


def main():
    cli_app()


if __name__ == "__main__":
    main()
