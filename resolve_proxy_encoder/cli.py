#!/usr/bin/env python3.6


import subprocess
import webbrowser

import typer
from pyfiglet import Figlet
from rich.pretty import pprint
from rich.prompt import Confirm

from resolve_proxy_encoder import link_proxies, resolve_queue_proxies, start_workers
from resolve_proxy_encoder.settings import app_settings

config = app_settings.get_user_settings()

# Print CLI title
fig = Figlet()
pprint(f"[green]{fig.renderText('Resolve Proxy Encoder')}[/]")

app = typer.Typer()

# Check before anything else
app_settings.check_settings()

@app.command()
def queue():
    """ 
    Queue proxies from the currently open 
    DaVinci Resolve timeline 
    """
    pprint("[green]Queuing proxies from Resolve's active timeline[/] :outbox_tray:")
    resolve_queue_proxies.main()

@app.command()
def link():
    """ 
    Manually link proxies from directory to
    source media in open DaVinci Resolve project 
    """

    link_proxies.main()

@app.command()
def work(number:int=0):
    """Prompt to start Celery workers on local machine"""
    if number > 0:
        pprint(f"[green]Starting workers! :construction_worker:[/]")
    pprint(f"[cyan]Starting worker launcher prompt :construction_worker:[/]")
    start_workers.main(number)

@app.command()
def purge():
    """ Purge all proxy jobs from all queues """

    if Confirm(
        "[yellow]Are you sure you want to purge all worker queues?"
        "All current jobs will be lost![/]"
    ):
        pprint("[green]Purging all worker queues[/] :fire:")
        subprocess.run(["celery_app", "-A", "proxy_encoder", "purge"])

@app.command()
def mon():
    """ 
    Launch Flower Celery monitor in default browser new window 
    """

    pprint("[green]Launching Flower celery monitor[/] :flower:")
    webbrowser.open_new(config['celery_settings']['flower_url'])

def main():
    app()
