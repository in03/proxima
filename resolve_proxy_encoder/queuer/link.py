#!/usr/bin/env python3.6
# Link proxies

import os
import tkinter
import tkinter.messagebox
import traceback
from tkinter import filedialog
from rich import print
from ..settings.manager import SettingsManager

config = SettingsManager()

root = tkinter.Tk()
root.withdraw()


def get_proxy_path():

    proxy_path_root = config["paths"]["proxy_path_root"]

    f = filedialog.askdirectory(initialdir=proxy_path_root, title="Link proxies")
    if f is None:
        print("User cancelled dialog. Exiting.")
        exit(0)
    return f


def recurse_dir(root):
    """Recursively search given directory for files
    and return full filepaths
    """

    all_files = [
        os.path.join(root, f) for root, dirs, files in os.walk(root) for f in files
    ]
    return all_files


def filter_files(dir_, acceptable_exts):
    """Filter files by allowed filetype"""

    # print(f"{Fore.CYAN}{timeline.GetName()} - Video track count: {track_len}")
    allowed = [x for x in dir_ if os.path.splitext(x) in acceptable_exts]
    return allowed


def get_track_items(timeline, track_type="video"):
    """Retrieve all video track items from a given timeline object"""

    track_len = timeline.GetTrackCount("video")

    if config["loglevel"] == "DEBUG":
        print(f"[cyan]{timeline.GetName()} - Video track count: {track_len}[/]")

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
    linked_clips = []

    for proxy in proxy_files:
        for clip in clips:

            proxy_name = os.path.splitext(os.path.basename(proxy))[0]
            if proxy in failed_proxies:
                if config["loglevel"] == "DEBUG":
                    print(f"[cyan]Skipping {proxy_name}, already failed.")
                break

            try:
                media_pool_item = clip.GetMediaPoolItem()
                path = media_pool_item.GetClipProperty("File Path")
                filename = os.path.splitext(os.path.basename(path))[0]

                if proxy_name.lower() in filename.lower():

                    print("[cyan]Found match:")
                    print(f"{proxy} &\n{path}")

                    if media_pool_item.LinkProxyMedia(proxy):

                        print(f"[green]Linked\n")
                        linked_proxies.append(proxy)
                        linked_clips.append(clip)

                    else:
                        print(f"[red]Failed link.\n")
                        failed_proxies.append(proxy)

            except AttributeError:

                if config["app"]["loglevel"] == "DEBUG":
                    print(
                        f"[yellow]{clip.GetName()} has no 'file path' attribute,"
                        + " probably Resolve internal media."
                    )

    return linked_proxies, failed_proxies


def link_proxies(project, proxy_files):
    """Attempts to match source media in active Resolve project
    with a list of filepaths to proxy files."""

    linked = []
    failed = []

    timelines = get_resolve_timelines(project)
    if not timelines:
        raise Exception("No timelines exist in current project.")

    # Get clips from all timelines.
    for timeline in timelines:

        timeline_data = get_timeline_data(timeline)
        clips = timeline_data["clips"]
        unlinked_source = [x for x in clips if x not in linked]

        if len(unlinked_source) == 0:
            if config["loglevel"] == "DEBUG":
                print(f"[yellow]No more clips to link in {timeline_data['name']}")
            continue
        else:
            print(f"[cyan]Searching timeline {timeline_data['name']}")

        unlinked_proxies = [x for x in proxy_files if x not in linked]
        print(f"Unlinked source count: {len(unlinked_source)}")
        print(f"Unlinked proxies count: {len(unlinked_proxies)}")

        if len(unlinked_proxies) == 0:
            print(f"[yellow]No more proxies to link in {timeline_data['name']}")
            return

        linked_, failed_ = _link_proxies(proxy_files, clips)

        linked.extend(linked_)
        failed.extend(failed_)

        if config["app"]["loglevel"] == "DEBUG":
            print(f"Linked: {linked}, Failed: {failed}")

    if len(failed) > 0:
        print(
            f"[red]The following files matched, but couldn't be linked. Suggest rerendering them:"
        )
        [print(os.path.basename(x)) for x in failed]
        print()

    return linked


def postencode_link(media_list):
    """Iterate through media mutated during script call, attempt to link the source media"""

    print(f"[cyan]Linking {len(media_list)} proxies.[/]")

    link_success = []
    link_fail = []

    # Iterate through all available proxies
    for media in media_list:
        proxy = media.get("Unlinked Proxy", None)
        if proxy == None:
            continue

        # Check they exist
        if not os.path.exists(proxy):
            tkinter.messagebox.showerror(
                title="Error linking proxy",
                message=f"Proxy media not found at '{proxy}'",
            )
            print(f"[red]Error linking proxy: Proxy media not found at '{proxy}'")
            continue

        else:
            media.update({"Unlinked Proxy": None})  # Set existing to none once linked

        media.update({"Proxy": "1280x720"})

        # Actually link proxies
        media_pool_item_obj = media["media_pool_item_obj"]
        if media_pool_item_obj.LinkProxyMedia(proxy):

            # TODO get this working!
            print(f"[green]Linked {media['File Name']}[/]")
            link_success.append(proxy)

        else:
            print(f"[red]Failed link.\n[/]")
            link_fail.append(proxy)

    if link_success:
        print(f"[green]Succeeeded linking: {len(link_success)}[/]")

    if link_fail:
        print(f"[red]Failed linking: {len(link_success)}[/]")

    # link_proxies(existing_proxies)

    print("\n")

    pre_len = len(media_list)
    media_list = [x for x in media_list if "Unlinked Proxy" not in x]
    post_len = len(media_list)
    print(f"{pre_len - post_len} proxy(s) linked, will not be queued.")
    print(f"[magenta]Queueing {post_len}[/]")
    print("\n")

    return media_list


def main():

    from .resolve import ResolveObjects

    try:

        r_ = ResolveObjects()
        proxy_dir = get_proxy_path()

        print(f"Passed directory: '{proxy_dir}'\n")

        all_files = recurse_dir(proxy_dir)
        proxy_files = filter_files(all_files, config["filters"]["acceptable_exts"])
        linked = link_proxies(r_.project, proxy_files)

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        tkinter.messagebox.showinfo("ERROR", tb)
        print("ERROR - " + str(e))


if __name__ == "__main__":
    main()
