import glob
import logging
import os
import pathlib
import shutil
import sys
from tkinter import E
from typing import Union

from rich import print as pprint
from rich.prompt import Confirm, Prompt

from resolve_proxy_encoder.queuer.resolve import ResolveObjects

from ..app.utils import core
from ..settings.manager import SettingsManager
from ..worker.celery import app
from . import link

settings = SettingsManager()
core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


# Set global flags
SOME_ACTION_TAKEN = False


def handle_file_collisions(media_list: list) -> list:
    """Increment output filenames if necessary to prevent file collisions"""

    def _increment_file_if_exist(input_path: str, increment_num: int = 1) -> str:
        """Increment the filename in a given filepath if it already exists

        Calls itself recursively in case any incremented files already exist.
        It should get the latest increment, i.e. 'filename_4.mp4'
        if 'filename_3.mp4', 'filename_2.mp4', 'filename_1.mp4' and 'filename.mp4'
        already exist.

        Args:
            input_path(str): full filepath to check.

        Returns:
            output_path(str): a modified output path, incremented.

        Raises:
            none
        """

        # Split filename, extension
        file_name, file_ext = os.path.splitext(input_path)

        # If file exists...
        if os.path.exists(input_path):

            # Check if already incremented
            if file_name.endswith(f"_{increment_num}"):

                # Increment again
                increment_num += 1
                _increment_file_if_exist(input_path, increment_num)

            else:
                # First increment
                file_name = file_name + "_1"

        return str(file_name + file_ext)

    media_list_ = []
    multiple_versions_count = 0

    for item in media_list:

        current_path = item.get("Expected Proxy Dir")

        # !ERROR: no expected path key
        if not current_path:
            logger.error(
                f"Expected proxy Dir was missing for an item: {item}. Skipping..."
            )
            continue

        final_path = _increment_file_if_exist(current_path)

        # Increment multiple version flag
        if final_path != current_path:
            multiple_versions_count += 1

        # !ERROR: Couldn't get final path
        if not final_path:
            logger.error(f"Couldn't get final path for an item: {item}. Skipping...")
            continue

    if multiple_versions_count:

        logger.warning(
            f"[yellow]{multiple_versions_count} files have outdated proxies!\n"
            + "Recommend manually deleting when possible.",
        )

    return media_list_


def handle_orphaned_proxies(media_list: list) -> list:
    """Prompts user to tidy orphaned proxies into the current proxy path structure.

    Orphans can become separated from a project if source media file-path structure changes.
    Finding them saves unncessary re-rendering time and lost disk space.

    Args:
        media_list: list of dictionary media items to check orphaned proxies for.

    Returns:
        media_list: unmodified `media_list`, returns for ease of chaining.
    """

    pprint(f"[cyan]Checking for orphaned proxies.")
    orphaned_proxies = []

    for clip in media_list:
        if clip["proxy"] != "None" or clip["proxy"] == "Offline":
            linked_proxy_path = os.path.splitext(clip["proxy_media_path"])
            linked_proxy_path[1].lower()

            file_path = clip["file_path"]
            p = pathlib.Path(file_path)

            # Append the source media relative path onto the proxy media path
            output_dir = os.path.join(
                settings["paths"]["proxy_path_root"],
                os.path.dirname(p.relative_to(*p.parts[:1])),
            )
            new_output_path = os.path.join(output_dir, os.path.basename(file_path))
            new_output_path = os.path.splitext(new_output_path)
            new_output_path[1].lower()

            if linked_proxy_path[0] != new_output_path[0]:

                # Rejoin extensions
                linked_proxy_path = "".join(linked_proxy_path)
                new_output_path = "".join(new_output_path)
                orphaned_proxies.append(
                    {
                        "old_path": linked_proxy_path,
                        "new_path": new_output_path,
                    }
                )

    if len(orphaned_proxies) > 0:

        pprint(f"[yellow]Orphaned proxies: {len(orphaned_proxies)}[/]")

        if Confirm.ask(
            f"[yellow]{len(orphaned_proxies)} clip(s) have orphaned proxy media."
            "Would you like to attempt to automatically move these proxies to the up-to-date proxy folder?\n\n"
            "For help, check 'Managing Proxies' in our YouTour documentation portal."
        ):

            pprint(f"[cyan]Moving orphaned proxies.[/]")
            for proxy in orphaned_proxies:

                output_folder = os.path.dirname(proxy["new_path"])
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)

                if os.path.exists(proxy["old_path"]):
                    shutil.move(proxy["old_path"], proxy["new_path"])
                else:
                    pprint(
                        f"{proxy['old_path']} doesn't exist. Most likely a parent directory rename created this orphan."
                    )
            pprint("\n")

        global SOME_ACTION_TAKEN
        SOME_ACTION_TAKEN = True

    return media_list


def handle_already_linked(
    media_list: list, offline_types: list = ["Offline", "None"]
) -> list:
    """Remove items from media-list that are already linked to a proxy.
    
    Since re-rendering linked clips is rarely desired behaviour, we remove them without prompting.
    If we do want to re-render proxies, we can unlink them from Resolve and we'll be prompted with the 
    'unlinked media' warning. By default if a proxy item is marked as 'Offline' it won't be removed
    since we most likely need to re-render it.

    Args: 
        media_list: list of dictionary media items to check for linked proxies.\
        retain_types: list of strings of `Proxy` types to keep in returned `media_list` even if linked.

    Returns:
        media_list: refined list of dictionary media items that are not linked to a proxy.
    """

    pprint(f"[cyan]Checking for source media with linked proxies.[/]")
    already_linked = [x for x in media_list if str(x["proxy"]) not in offline_types]

    if len(already_linked) > 0:

        pprint(f"[yellow]Skipping {len(already_linked)} already linked.[/]")
        media_list = [x for x in media_list if x not in already_linked]
        pprint("\n")

    return media_list


def handle_offline_proxies(media_list: list) -> list:
    """Prompt to rerender proxies that are 'linked' but their media does not exist.

    Resolve refers to proxies that are linked but inaccessible as 'offline'.
    This prompt can warn users to find that media if it's missing, or rerender if intentionally unavailable.

    Args:
        media_list: list of dictionary media items to check for `Proxy` value.

    Returns:
        media_list: Modified list of dictionary media items with `Proxy` set to `None` if re-rendering.
    """

    pprint("\n")
    pprint(f"[cyan]Checking for offline proxies[/]")
    offline_proxies = [x for x in media_list if x["proxy"] == "Offline"]

    if len(offline_proxies) > 0:

        pprint(f"[cyan]Offline proxies: {len(offline_proxies)}[/]")

        for offline_proxy in offline_proxies:

            answer = Prompt.ask(
                f"'{offline_proxy}' [yellow]is offline.\n"
                "Would you like to re-render it?[/] [magenta][Y/N or All)]"
            )

            if answer.lower().startswith("y"):
                pprint(f"[yellow]Queuing '{offline_proxy}' for re-render")
                [
                    x["proxy"].update("None")
                    for x in media_list
                    if x["file_path"] == offline_proxy["file_path"]
                ]

            elif answer.lower().startswith("a"):

                pprint(
                    f"[yellow]Queuing {len(offline_proxies)} offline proxies for re-render"
                )
                [x["proxy"].update("None") for x in media_list if x == "Offline"]

        global SOME_ACTION_TAKEN
        SOME_ACTION_TAKEN = True

    return media_list


def handle_existing_unlinked(media_list: list) -> list:

    """Prompts user to either link or re-render unlinked proxy media that exists in the expected location.

    This handler will run if proxies are either unlinked at some point or were never linked after proxies finished rendering.

    Args:
        media_list: list of dictionaries with media items to check `Expected Proxy Dir` variable on.

    Returns:
        media_list: refined list of dictionaries with media items that do not have linked proxies.
    """

    pprint(f"[cyan]Checking for existing, unlinked media.")

    def get_newest_proxy_file(expected_path: str) -> Union[str, None]:
        """Get the last modified proxy file if multiple variants of same filename exist.

        Args:
            proxy_dir(str): The path all proxies for comparison are located.

        Returns:
            final_proxy_path(str): The file path to the matching proxy file that was last modified.

        """

        expected_filename = os.path.basename(expected_path)

        # Fetch paths of all possible variants of source filename
        matching_proxy_files = glob.glob(expected_path + "*.*")

        if not len(matching_proxy_files):
            logger.info(f"[yellow]No existing proxies found for '{expected_filename}'")
            return None

        if len(matching_proxy_files) == 1:
            return os.path.normpath(matching_proxy_files[0])

        # Sort matching proxy files by last modified in descending order
        matching_proxy_files.sort(key=os.path.getmtime, reverse=True)

        # Assume we want newest matching file
        final_proxy_path = matching_proxy_files[0]
        final_proxy_filename = os.path.basename(final_proxy_path)

        logger.warning(
            f"[yellow]Found {len(matching_proxy_files)} existing matches for '{expected_filename}'[/]\n"
            + f"[cyan]Using newest: '{os.path.basename(final_proxy_filename)}'[/]"
        )

        return os.path.normpath(final_proxy_path)

    existing_unlinked = []

    # Iterate media list
    for media in media_list:

        if media["proxy"] == "None":

            expected_proxy_dir = media["expected_proxy_dir"]
            source_media_basename = os.path.splitext(
                os.path.basename(media["file_path"])
            )[0]
            expected_proxy_file = os.path.join(
                expected_proxy_dir, source_media_basename
            )
            expected_proxy_file = os.path.splitext(expected_proxy_file)[0]
            existing_proxy_file = get_newest_proxy_file(expected_proxy_file)

            if existing_proxy_file:

                logger.debug(f"[magenta]Adding unlinked proxy: {existing_proxy_file}")
                media.update({"unlinked_proxy": existing_proxy_file})
                existing_unlinked.append(existing_proxy_file)

    # If any unlinked, prompt for linking
    if len(existing_unlinked) > 0:

        global SOME_ACTION_TAKEN
        SOME_ACTION_TAKEN = True

        r_ = ResolveObjects()

        pprint(f"\n[yellow]Found {len(existing_unlinked)} unlinked[/]")

        if Confirm.ask(
            f"{len(existing_unlinked)} clip(s) have existing but unlinked proxy media. "
            "Would you like to link them? If you select 'No' they will be re-rendered."
        ):

            return link.link_proxies_with_mpi(media_list)

        else:

            pprint(
                f"[yellow]Existing proxies will be [bold]OVERWRITTEN![/bold][/yellow]"
            )

    return media_list


def handle_final_queuable(jobs: list):
    """Final prompt to confirm number queueable or warn if none.

    Args:
        media_list: list of dictionary media items to check length for.

    Returns:
        None: No need to chain anything here.

    Raises:
        TypeError: if media_list is not a list
    """

    if len(jobs) == 0:

        global SOME_ACTION_TAKEN
        if not SOME_ACTION_TAKEN:

            pprint(
                "[green]Looks like all your media is already linked.[/]\n"
                "[magenta italic]If you want to re-rerender proxies, unlink them within Resolve and try again."
            )

            core.app_exit(0, -1)

    # Final Prompt confirm
    if not Confirm.ask(
        f"[bold][green]Go time![/bold] {len(jobs)} to queue. Sound good?[/]"
    ):
        core.app_exit(0)

    return
