#!/usr/bin/env python3.6

import json
import logging
import os
import time

from celery import group
from rich import print
from rich.console import Console, Group
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.live import Live

from ..app.broker import TaskTracker
from ..app.utils import core
from ..settings.manager import SettingsManager
from ..worker.tasks.encode.tasks import encode_proxy
from ..worker.celery import app as celery_app
from . import handlers, link, resolve

settings = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])

# Set global flags
SOME_ACTION_TAKEN = False


def add_queuer_data(jobs, **kwargs):
    """
    Extend jobs with relevant queuer data

    Args:
        **kwargs - any keyword arguments to pass with the tasks to the worker\n
         queuer-side configuration extra Resolve variables, etc can be passed

    Returns:
        jobs - the original jobs with added data

    Raises:
        nothing
    """

    jobs = [dict(item, **kwargs) for item in jobs]
    return jobs


def queue_tasks(tasks):
    """Block until all queued tasks finish, notify results."""

    # Wrap task objects in Celery task function
    callable_tasks = [encode_proxy.s(x) for x in tasks]
    logger.debug(f"[magenta]callable_tasks:[/] {callable_tasks}")

    # Create task group to retrieve job results as batch
    task_group = group(callable_tasks)

    # Subscribe to progress channel
    tt = TaskTracker(settings)
    tt.subscribe()

    # Queue job
    results = task_group.apply_async(expires=settings['broker']['job_expires'])
    logger.debug(f"[cyan]Queued tasks {results}[/]")

    return tt, callable_tasks, results


def report_progress(tt, callable_tasks, results):

    # Define various progress bar formats
    worker_spinner = Progress(
        SpinnerColumn(),
        # TODO: Get individual worker names instead of host machines
        # labels: enhancement
        TextColumn("[cyan]Using {task.fields[worker_count]} host-machines"),
    )

    average_progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("[yellow]ETA:[/]"),
        TimeRemainingColumn(),
    )

    overall_progress = Progress(
        TextColumn("[cyan]{task.description}"),
        # TODO: Fix bar column not lining up with task_progress bars
        # Maybe we can make a spacer text column for all the bars and truncate long filenames with [...]?
        # labels: bug
        BarColumn(),
        TextColumn("[cyan]({task.completed} of {task.total})"),
    )

    # Create group of renderables
    progress_group = Group(
        worker_spinner,
        average_progress,
        overall_progress,
    )

    worker_id = worker_spinner.add_task(
        description="Active worker count", worker_count=0
    )

    average_id = average_progress.add_task(
        description="Average task progress",
        total=len(callable_tasks),
    )

    overall_id = overall_progress.add_task(
        description="Total task progress",
        total=len(callable_tasks),
    )

    # If not finished, report progress
    progress_vals = {}
    active_workers = []
    completed_tasks = 0

    with Live(progress_group):

        while not results.ready():

            # Update overall progress
            tt_data = tt.get_data(group_id=results.id)
            if tt_data:

                # Update overall task progress
                task_event = tt_data.get("task-event")
                if task_event:

                    # Finished a task, update completed
                    if task_event["status"] in ["SUCCESS", "FAILURE"]:

                        completed_tasks = completed_tasks + 1
                        overall_progress.update(
                            task_id=overall_id,
                            completed=completed_tasks,
                            total=len(callable_tasks),
                        )

                # TODO: Check this works!
                # Also, rework the redis pub/sub to use callbacks

                # If we've got task progress, update
                progress = tt_data.get("task-progress")
                if progress:

                    # Update progress for correct task
                    progress_vals.update({progress.task_id: progress.seconds_processed})

                    # Get up-to-date average
                    prog_list = list(progress_vals.values())
                    prog_sum = sum(prog_list)
                    avg_progress = (prog_sum / callable_tasks)

                    # Update average progress bar
                    average_progress.update(
                            task_id=average_id,
                            completed=avg_progress,
                        )

                    # Add new workers
                    if progress["worker_name"] not in active_workers:
                        active_workers.append(progress["worker_name"])

                        # Update worker spinner
                        worker_spinner.update(
                            task_id=worker_id,
                            worker_count=len(active_workers),
                        )

        # Hide the progress bars after finish
        worker_spinner.update(task_id=worker_id, visible=False)
        # average_progress.update(task_id=average_id, visible=False)
        # overall_progress.update(task_id=overall_id, visible=False)

    # Notify failed
    if results.failed():
        fail_message = ("Some videos failed to encode!")
        print("[red]fail_message[/]")
        core.notify(fail_message)

    # Notify complete
    complete_message = f"Completed encoding {results.completed_count()} proxies."
    print(f"[green]{complete_message}[/]")
    print("\n")

    core.notify(complete_message)

    joined_results = results.join()
    return joined_results


def main():
    """Main function"""

    r_ = resolve.ResolveObjects()
    project_name = r_.project.GetName()
    timeline_name = r_.timeline.GetName()

    print("\n")
    print(f"[cyan]Working on: '{r_.project.GetName()}[/]'")
    print("\n")

    # Lets make it happen!
    track_items = resolve.get_video_track_items(r_.timeline)
    media_pool_items = resolve.get_media_pool_items(track_items)
    jobs = resolve.get_resolve_proxy_jobs(media_pool_items)

    # Prompt user for intervention if necessary
    print()
    jobs = handlers.handle_already_linked(jobs, unlinked_types=["Offline", "None"])
    logger.debug(f"[magenta]Remaining queuable:[/]\n{[x['file_name'] for x in jobs]}")

    print()
    jobs = handlers.handle_existing_unlinked(jobs, unlinked_types=["Offline", "None"])
    logger.debug(f"[magenta]Remaining queuable:[/]\n{[x['file_name'] for x in jobs]}")

    print()
    jobs = handlers.handle_offline_proxies(jobs)
    logger.debug(f"[magenta]Remaining queuable:[/]\n{[x['file_name'] for x in jobs]}")

    print("\n")

    # Alert user final queuable. Confirm.
    handlers.handle_final_queuable(jobs)

    # Get output paths for queueable jobs
    for x in jobs:

        proxy_output_path = os.path.join(
            x["proxy_dir"],
            os.path.splitext(x["file_name"])[0]
            + settings["proxy"]["ext"],  # Output ext, differs from source
        )

        x.update({"proxy_media_path": proxy_output_path})

        logger.debug(
            "[magenta]Set proxy_media_path to output path:[/]\n"
            f"'{x['proxy_media_path']}'\n"
        )

    # Celery can't accept MPI (pyremoteobj)
    # Convert to string for later reference
    jobs_with_mpi = []
    for x in jobs:
        jobs_with_mpi.append({str(x["media_pool_item"]): x["media_pool_item"]})
        x.update({"media_pool_item": str(x["media_pool_item"])})

    tasks = add_queuer_data(
        jobs,
        project=project_name,
        timeline=timeline_name,
        proxy_settings=settings["proxy"],
        paths_settings=settings["paths"],
    )

    print("\n")

    core.notify(f"Started encoding job '{project_name} - {timeline_name}'")
    # print(f"[yellow]Waiting for job to finish. Feel free to minimize.[/]")

    # Queue tasks to workers and track task progress
    task_tracker, callable_tasks, results = queue_tasks(tasks)
    final_results = report_progress(task_tracker, callable_tasks, results)

    # Get media pool items back
    logger.debug(f"[magenta]Restoring media-pool-items[/]")

    for x, y in zip(jobs, jobs_with_mpi):
        for k, v in y.items():
            assert hasattr(v, "GetClipProperty()")
            if x["media_pool_item"] == k:
                x.update({"media_pool_item": v})

    try:

        unlinkable = link.link_proxies_with_mpi(
            jobs,
            linkable_types=["None"],
            prompt_rerender=False,
        )
        assert len(unlinkable) == 0

    except Exception as e:

        logger.error(f"[red]Couldn't link jobs. Link manually.[/]\nError: {e}")
        core.app_exit(1, -1)

    finally:
        print("[bold][green]All linked up![/bold] Nothing to queue[/] :link:")
        core.app_exit(0)


if __name__ == "__main__":
    main()
