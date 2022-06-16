#!/usr/bin/env python3.6

import logging
import os

from celery import group
from rich import print as print

from ..app.utils import core
from ..settings.manager import SettingsManager
from ..worker.tasks.encode.tasks import encode_proxy
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


def queue_jobs(jobs):
    """Send jobs as a Celery 'group'"""

    # Wrap job objects in Celery task function
    callable_tasks = [encode_proxy.s(x) for x in jobs]
    logger.debug(f"[magenta]callable_tasks:[/] {callable_tasks}")

    # Create job group to retrieve job results as batch
    task_group = group(callable_tasks)

    # Queue job
    queued_group = task_group.apply_async()
    logger.debug(f"[cyan]Queued tasks {queued_group}[/]")

    return queued_group


def wait_jobs(jobs):
    """Block until all queued jobs finish, notify results."""

    result = jobs.join()

    # Notify failed
    if jobs.failed():
        fail_message = (
            "Some videos failed to encode!"
            + f"Check flower dashboard at address: {settings['celery']['flower_url']}."
        )
        print("[red]fail_message[/]")
        core.notify(fail_message)

    # Notify complete
    complete_message = f"Completed encoding {jobs.completed_count()} proxies."
    print(f"[green]{complete_message}[/]")
    print("\n")

    core.notify(complete_message)

    return result


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
    for job in jobs:

        proxy_output_path = os.path.join(job["proxy_dir"], job["file_name"])
        job.update({"proxy_media_path": proxy_output_path})

        logger.debug(
            "[magenta]Set proxy_media_path to output path:[/]\n"
            f"'{job['proxy_media_path']}'\n"
        )

    # Celery can't accept MPI (pyremoteobj)
    # Convert to string for later reference
    jobs_with_mpi = []
    for job in jobs:
        jobs_with_mpi.append({str(job["media_pool_item"]): job["media_pool_item"]})
        job.update({"media_pool_item": str(job["media_pool_item"])})

    tasks = add_queuer_data(
        jobs,
        project=project_name,
        timeline=timeline_name,
        proxy_settings=settings["proxy"],
        paths_settings=settings["paths"],
    )

    print("\n")

    job_group = queue_jobs(tasks)

    core.notify(f"Started encoding job '{project_name} - {timeline_name}'")
    print(f"[yellow]Waiting for job to finish. Feel free to minimize.[/]")
    wait_jobs(job_group)

    # Get media pool items back
    for x in jobs:
        for y in jobs_with_mpi:
            for k, v in y.items():
                if x["media_pool_item"] == k:
                    x.update({"media_pool_item": v})

    logger.debug(f"[magenta]Jobs with restored MPIs:[/]\n{jobs}")

    try:

        unlinkable = link.link_proxies_with_mpi(
            jobs,
            linkable_types=["None"],
            prompt_rerender=False,
        )
        # We shouldn't have any leftover proxies!
        assert len(unlinkable) == 0

    except Exception as e:

        logger.error(f"[red]Couldn't link jobs. Link manually.[/]\nError: {e}")
        core.app_exit(1, -1)

    finally:
        print("[bold][green]All linked up![/bold] Nothing to queue[/] :link:")
        core.app_exit(0)


if __name__ == "__main__":
    main()
