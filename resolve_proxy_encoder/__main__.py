#!/usr/bin/env python3.6

import typer

from . start_workers import launch_workers
from . import link_proxies
from . import resolve_queue_proxies

app = typer.Typer()

@app.command()
def queue():
    """ 
    Queue proxies from the currently open 
    DaVinci Resolve timeline 
    """
    resolve_queue_proxies()

@app.command()
def link():
    """ 
    Manually link proxies from directory to
    source media in open DaVinci Resolve project 
    """
    link_proxies()

@app.command()
def work(number:int=0):
    """Prompt to start Celery workers on local machine"""
    launch_workers(number)

if __name__ == "__main__":
    app()