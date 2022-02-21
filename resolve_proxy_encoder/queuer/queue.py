#!/usr/bin/env python3.6

import logging
import os
import tkinter
import tkinter.messagebox
import handlers

from app.utils import core
from celery import group
from rich import print
from settings.manager import SettingsManager
from worker.tasks.encode.tasks import encode_proxy

from queuer import link, resolve

config = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)

# Set global flags
SOME_ACTION_TAKEN = False
tk_root = tkinter.Tk()
tk_root.withdraw()


def create_tasks(clips, **kwargs):
    """Create metadata dictionaries to send as Celery tasks'"""

    # Append project details to each clip
    tasks = [dict(item, **kwargs) for item in clips]
    return tasks


def queue_job(tasks):
    """Send tasks as a celery job 'group'"""

    # Wrap job object in task function
    callable_tasks = [encode_proxy.s(x) for x in tasks]
    logger.debug(f"callable_tasks: {callable_tasks}")

    # Create job group to retrieve job results as batch
    job = group(callable_tasks)

    # Queue job
    queued_job = job.apply_async()
    logger.info(f"[cyan]Queued job {queued_job}[/]")

    return queued_job


def wait_encode(job):
    """Block until all queued jobs finish, notify results."""

    result = job.join()

    # Notify failed
    if job.failed():
        fail_message = (
            "Some videos failed to encode!"
            + f"Check flower dashboard at address: {config['celery']['flower_url']}."
        )
        print("[red]fail_message[/]")
        core.notify(fail_message)

    # Notify complete
    complete_message = f"Completed encoding {job.completed_count()} proxies."
    print(f"[green]{complete_message}[/]")
    print("\n")

    core.notify(complete_message)

    return result


# TODO: Need to get new search and link working
# Legacy link is the original code and it's soooo bad.
# I haven't looked at it in ages. But then I bit off more than I could
# chew working on this. Find a middle ground!
# labels: bug


def legacy_link(media_list):
    """This is sooooo dank. But it's the only way that works atm."""

    print(f"[cyan]Linking {len(media_list)} proxies.[/]")
    existing_proxies = []

    for media in media_list:
        proxy = media.get("Unlinked Proxy", None)
        if proxy == None:
            continue

        existing_proxies.append(proxy)

        if not os.path.exists(proxy):
            tkinter.messagebox.showerror(
                title="Error linking proxy",
                message=f"Proxy media not found at '{proxy}'",
            )
            print(f"[red]Error linking proxy: Proxy media not found at '{proxy}'[/]")
            continue

        else:
            media.update({"Unlinked Proxy": None})  # Set existing to none once linked

        media.update({"Proxy": "1280x720"})

    link.link_proxies(existing_proxies)

    print("\n")

    pre_len = len(media_list)
    media_list = [x for x in media_list if "Unlinked Proxy" not in x]
    post_len = len(media_list)
    print(f"{pre_len - post_len} proxy(s) linked, will not be queued.")
    print(f"[magenta]Queueing {post_len}[/]")
    print("\n")

    return media_list


def main():
    """Main function"""

    r_ = resolve.ResolveObjects()
    project_name = r_.project.GetName()
    timeline_name = r_.timeline.GetName()

    print(f"[cyan]Working on: {r_.project.GetName()}[/]")
    handlers.handle_workers()
    print("\n")

    # Lets make it happen!
    track_items = resolve.get_video_track_items(r_.timeline)
    media_pool_items = resolve.get_media_pool_items(track_items)
    source_metadata = resolve.get_source_metadata(media_pool_items)

    print("\n")

    # TODO: Neither var name `clips` nor `source_metadata` are great
    # Decide a variable name to use consistently!
    # labels: enhancement
    clips = source_metadata

    # Prompt user for intervention if necessary
    clips = handlers.handle_already_linked(clips, ["Offline", "None"])
    clips = handlers.handle_offline_proxies(clips)
    clips = handlers.handle_existing_unlinked(clips)

    handlers.handle_final_queuable(clips)

    tasks = create_tasks(
        clips,
        project=project_name,
        timeline=timeline_name,
    )

    job = queue_job(tasks)

    core.notify(f"Started encoding job '{project_name} - {timeline_name}'")
    print(f"[yellow]Waiting for job to finish. Feel free to minimize.[/]")
    wait_encode(job)

    # ATTEMPT POST ENCODE LINK
    try:

        clips = link._legacy_link(clips)
        core.app_exit(0)

    except:

        print("[red]Couldn't link clips. Link manually...[/]")
        core.app_exit(1, -1)


if __name__ == "__main__":
    main()
