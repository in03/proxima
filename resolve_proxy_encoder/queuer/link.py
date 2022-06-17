#!/usr/bin/env python3.6
# Link proxies

import logging
import os
from typing import Tuple, Union

from rich import print as pprint
from rich.console import Console
from rich.prompt import Confirm, Prompt

from ..app.utils import core
from ..settings.manager import SettingsManager
from .resolve import ResolveObjects

console = Console()
settings = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


def get_proxy_path():

    # TODO: Allow linking via custom path passed by Typer or use default proxy dir
    # labels: enhancement

    f = Prompt.ask("Enter path to search for proxies")
    if f is None:
        pprint("User cancelled. Exiting.")
        core.app_exit(0, 0)
    return f


def recurse_dir(root):
    """Recursively search given directory for files
    and return full filepaths
    """

    all_files = [
        os.path.join(root, f) for root, dirs, files in os.walk(root) for f in files
    ]
    pprint(f"Found {len(all_files)} files in folder {root}")
    return all_files


def filter_files(dir_, extension_whitelist):
    """Filter files by allowed filetype"""

    # pprint(f"{timeline.GetName()} - Video track count: {track_len}")
    allowed = [x for x in dir_ if os.path.splitext(x) in extension_whitelist]
    return allowed


def get_track_items(timeline, track_type="video"):
    """Retrieve all video track items from a given timeline object"""

    track_len = timeline.GetTrackCount("video")
    logger.debug(f"[cyan]{timeline.GetName()} - Video track count: {track_len}[/]")

    items = []

    for i in range(track_len):
        i += 1  # Track index starts at one...
        items.extend(timeline.GetItemListInTrack(track_type, i))

    return items


def get_resolve_timelines(project, active_timeline_first=True):
    """Return a list of all Resolve timeline objects in current project."""

    timelines = []

    timeline_len = project.GetTimelineCount()
    if timeline_len > 0:

        for i in range(1, timeline_len + 1):
            timeline = project.GetTimelineByIndex(i)
            timelines.append(timeline)

        if active_timeline_first:
            active = project.GetCurrentTimeline().GetName()  # Get active timeline
            timeline_names = [x.GetName() for x in timelines]
            active_i = timeline_names.index(
                active
            )  # It's already in the list, find it's index
            timelines.insert(
                0, timelines.pop(active_i)
            )  # Move it to the front, indexing should be the same as name list
    else:
        return False

    return timelines


def get_timeline_data(timeline):
    """Return a dictionary containing timeline names,
    their tracks, clips media paths, etc.
    """

    clips = get_track_items(timeline, track_type="video")
    data = {
        "timeline": timeline,
        "name": timeline.GetName(),
        "track count": timeline.GetTrackCount(),
        "clips": clips,
    }

    return data


def _link_proxies(proxy_files, clips):
    """Actual linking function.
    Matches filenames between lists of paths.
    'clips' actually needs to be a Resolve timeline item object.
    """

    linked_proxies = []
    failed_proxies = []

    for proxy in proxy_files:
        for clip in clips:

            proxy_name = os.path.splitext(os.path.basename(proxy))[0]
            if proxy in failed_proxies:
                logger.warning(f"[yellow]Skipping {proxy_name}, already failed.")
                break

            try:
                media_pool_item = clip.GetMediaPoolItem()
                path = media_pool_item.GetClipProperty("File Path")
                filename = os.path.splitext(os.path.basename(path))[0]

                if proxy_name.lower() in filename.lower():

                    logger.info("[cyan]Found match:\n" f"- '{proxy}' \n- '{path}'")

                    if media_pool_item.LinkProxyMedia(proxy):

                        logger.info(f"[green]:heavy_check_mark: Linked \n")
                        linked_proxies.append(proxy)

                    else:
                        logger.error(f"[red bold]:x: Failed link.\n")
                        failed_proxies.append(proxy)

                    break

            except AttributeError:
                logger.debug(
                    f"[magenta]{clip.GetName()} has no 'file path' attribute,"
                    + " probably Resolve internal media."
                )

    return linked_proxies, failed_proxies


def find_and_link_proxies(project, proxy_files) -> Tuple[list, list]:
    """Attempts to match source media in active Resolve project
    with a list of filepaths to proxy files."""

    linked = []
    failed = []

    timelines = get_resolve_timelines(project)

    if not timelines:

        logger.error("[red]No timelines exist in current project.[/]")
        return linked, failed

    # Get clips from all timelines.
    for timeline in timelines:

        timeline_data = get_timeline_data(timeline)
        clips = timeline_data["clips"]
        unlinked_source = [x for x in clips if x not in linked]

        if not unlinked_source:
            logger.info(f" -> [yellow]No more clips to link in {timeline_data['name']}")
            continue
        else:
            pprint("\n")
            console.rule(
                f":mag_right: [cyan bold]Searching timeline '{timeline_data['name']}'",
                align="left",
            )
            pprint("\n")

        unlinked_proxies = [x for x in proxy_files if x not in linked]
        logger.info(f"Unlinked source count: {len(unlinked_source)}")
        logger.info(f"Unlinked proxies count: {len(unlinked_proxies)}")

        if not unlinked_proxies:
            logger.info(f"[green]No more proxies to link[/]")
            break

        pprint()

        print(f"Proxy files for link: {proxy_files}")
        print(f"Source media to link with: {clips}")

        # This inter-function nested loop thing is a little dank.
        linked_, failed_ = _link_proxies(proxy_files, clips)
        if len(linked_) + len(failed_) == len(proxy_files):
            break

        # Update lists for each timeline
        linked.extend(linked_)
        failed.extend(failed_)

    if linked:

        logger.info(f"[green]Link success:[/] {len(linked)}")

    if failed:

        logger.error(f"[red]Link fail:[/]{len(failed)}")
        failed_paths = [(os.path.basename(x)) for x in failed]
        logger.error(
            f"[red]The following files matched, but couldn't be linked. Suggest re-rendering them:[/]\n{failed_paths}"
        )

    return linked, failed


def link_proxies_with_mpi(
    jobs,
    linkable_types: list = ["Offline", "None"],
    prompt_reiterate=True,
    prompt_rerender=False,
):
    """
    Iterate through media list and link each finished proxy with its media pool item.

    Args:
        jobs (list of dicts): queuable jobs with project, timeline and setting metadata
        linkable_types (list, optional): List of job `proxy_status` values to attempt link on. Defaults to ["Offline", "None"].
        prompt_reiterate(bool, optional): If any links fail, prompt the user to fetch media pool items again by reiterating timelines.
        If prompt_rerender is enabled, prompt_reiterate runs first.
        prompt_rerender (bool, optional): If any links fail, prompt the user to re-queue them. Defaults to False.

    Returns:
        remaining_jobs (list of cits): the remaining queuable jobs that haven't been linked
    """

    logger.info(f"[cyan]Linking {len(jobs)} proxies[/]")

    link_success = []
    link_fail = []

    # Iterate through all available proxies
    for job in jobs:

        logger.debug(f"[magenta]Attempting to link job:[/]\n {job}")

        if job["proxy_status"] not in linkable_types:
            continue

        # TODO: Should probably use MediaInfo here instead of hardcode

        # We only define the vertical res in `user_settings` so we can preserve aspect ratio.
        # To get the proper resolution, we'd have to get the original file resolution.
        # labels: enhancement

        job.update({"proxy_status": "1280x720"})

        logger.info(f"[cyan]:link: '{job['file_name']}'")

        # Actually link proxies
        if job["media_pool_item"].LinkProxyMedia(job["proxy_media_path"]):

            logger.info(f"[green bold]:heavy_check_mark: Linked\n")
            link_success.append(job)

        else:
            logger.error(f"[red bold]:x: Failed link'\n")
            link_fail.append(job)

    if link_success:
        logger.debug(f"[magenta]Total link success:[/] {len(link_success)}")

    if link_fail:
        logger.error(f"[red]{len(link_fail)} proxies failed to link!")

        if prompt_reiterate:

            if Confirm.ask(
                f"[yellow]If you've changed projects since queuing\n"
                "you'll have to run a comprehensive search. Run now?"
            ):

                r_ = ResolveObjects()
                find_and_link_proxies(r_.project, [x["proxy_media_path"] for x in jobs])

                remaining_jobs = [x for x in jobs if x not in link_success]
                return remaining_jobs

        if prompt_rerender:

            if Confirm.ask(
                f"[yellow]Couldn't link proxies. Would you like to re-render them?"
            ):
                # Remove offline status, redefine media list
                for x in jobs:
                    if x in link_fail:
                        x["proxy_status"] = "None"

                remaining_jobs = [x for x in jobs if x not in link_success]
                return remaining_jobs

    # Queue only those that remain
    remaining_jobs = [
        x for x in jobs if all([x not in link_success, x not in link_fail])
    ]

    logger.debug(f"[magenta]Remaining unlinked jobs:\n{remaining_jobs}")
    return remaining_jobs


def main():

    from .resolve import ResolveObjects

    try:

        r_ = ResolveObjects()
        proxy_dir = get_proxy_path()

        pprint(f"Passed directory: '{proxy_dir}'\n")

        all_files = recurse_dir(proxy_dir)
        proxy_files = filter_files(
            all_files, settings["filters"]["extension_whitelist"]
        )
        linked = find_and_link_proxies(r_.project, proxy_files)

    except Exception as e:
        pprint("ERROR - " + str(e))


if __name__ == "__main__":
    main()
