import imp
import logging
import os
import sys

from app.utils import core
from settings.manager import SettingsManager

config = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)


class ResolveObjects:
    def __init__(self):
        self._populate_variables()

    def _get_resolve(self):

        ext = ".so"
        if sys.platform.startswith("darwin"):
            path = "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            path = "C:\\Program Files\\Blackmagic Design\\DaVinci Resolve\\"
            ext = ".dll"
        elif sys.platform.startswith("linux"):
            path = "/opt/resolve/libs/Fusion/"
        else:
            raise Exception("Unsupported system! " + sys.platform)

        bmd = imp.load_dynamic("fusionscript", path + "fusionscript" + ext)
        resolve = bmd.scriptapp("Resolve")

        if not resolve:
            return None

        try:
            sys.modules[__name__] = resolve
        except ImportError:
            return None

        return resolve

    def _populate_variables(self):

        try:

            self.resolve = self._get_resolve()
            if self.resolve is None:
                raise TypeError

        except:

            logger.warning(
                "[red] :warning: Couldn't access the Resolve Python API. Is DaVinci Resolve running?[/]"
            )
            core.app_exit(1, -1)

        try:

            self.project = self.resolve.GetProjectManager().GetCurrentProject()
            if self.project is None:
                raise TypeError

        except:

            logger.warning(
                "[red] :warning: Couldn't get current project. Is a project open in Resolve?[/]"
            )
            core.app_exit(1, -1)

        try:

            self.timeline = self.project.GetCurrentTimeline()
            if self.timeline is None:
                raise TypeError
        except:

            logger.warning(
                "[red] :warning: Couldn't get current timeline. Is a timeline open in Resolve?[/]"
            )
            core.app_exit(1, -1)

        try:

            self.media_pool = self.project.GetMediaPool()
            if self.media_pool is None:
                raise TypeError

        except:

            logger.warning("[red] :warning: Couldn't get Resolve's media pool.[/]")
            core.app_exit(1, -1)


def get_video_track_items(timeline):
    """Get all video track items from the provided timeline"""

    all_track_items = []

    # Get count of tracks (index) in active timeline
    track_len = timeline.GetTrackCount("video")
    print(f"[green]Video track count: {track_len}[/]")

    # For each track in timeline (using index)
    for i in range(1, track_len + 1):

        # Get items
        track_items = timeline.GetItemListInTrack("video", i)

        if track_items is None:
            print(f"[yellow]No items found in track {i}[/]")
            continue

        else:
            all_track_items.append(track_items)

    return all_track_items


def get_media_pool_items(track_items):
    """Return media pool items for all track items"""

    all_media_pool_items = []

    for track in track_items:
        for item in track:
            media_item = item.GetMediaPoolItem()
            all_media_pool_items.append(media_item)

    return all_media_pool_items


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


def get_source_metadata(media_pool_items):
    """Return source metadata for each media pool item that passes configured criteria.

    each media pool item must meet the following criteria:
        - return valid clip properties (needed for encoding, internal track items don't have them)
        - whitelisted extension (e.g, BRAW performs fine without proxies)
        - whitelisted framerate (optional) FFmpeg should handle most

    Args:
        - media_pool_items: list of Resolve API media pool items

    Returns:
        - filtered_metadata: a list of dictionaries containing all valid media and its Resolve-given properties.

    Raises:
        - none

    """

    # Lists
    filtered_metadata = []

    # Prevent filtering same media item multiple times
    # since multiple clips can have same source media
    seen_item = []

    for media_pool_item in media_pool_items:

        # Check media pool item is valid, get UUID
        try:

            mpi_uuid = str(media_pool_item).split("UUID:")[1].split("]")[0]

        except:

            logger.debug(
                f"[magenta]Media Pool Item: 'None'[/]\n"
                + f"[yellow]Invalid item: has no UUID[/]\n",
                extra={"markup": True},
            )
            continue

        if str(media_pool_item) in seen_item:

            logger.debug(
                f"[magenta]Media Pool Item: {mpi_uuid}[/]\n"
                + "[yellow]Already seen media pool item. Skipping...[/]\n",
                extra={"markup": True},
            )
            continue

        else:

            # Add first encounter to list for comparison
            seen_item.append(str(media_pool_item))

        # Check media pool item has clip properties
        if not hasattr(media_pool_item, "GetClipProperty()"):

            logger.debug(
                f"[magenta]Media Pool Item: {mpi_uuid}[/]\n"
                + "[yellow]Media pool item has no clip properties. Skipping...[/]\n",
                extra={"markup": True},
            )
            continue

        # Get source metadata, path, extension
        source_metadata = media_pool_item.GetClipProperty()
        source_path = source_metadata["File Path"]
        source_ext = os.path.splitext(source_path)[1].lower()

        # Might still get media that has clip properties, but empty attributes
        # Should only be internally generated media that returns this way
        if source_path is "":

            logger.debug(
                f"[magenta]Media Pool Item: {mpi_uuid}[/]\n"
                + f"clip properties did not return a valid filepath. Skipping...\n",
                extra={"markup": True},
            )
            continue

        # Filter extension
        if source_ext not in config["filters"]["extension_whitelist"]:

            logger.warning(
                f"[magenta]Media Pool Item: {mpi_uuid}[/]\n"
                + f"[yellow]Ignoring non-whitelisted file extension: '{source_ext}'[/]\n"
                + f"from '{source_metadata['File Path']}'[/]\n",
                extra={"markup": True},
            )
            continue

        # Filter framerate
        source_framerate = source_metadata["FPS"]
        if config["filters"]["use_framerate_whitelist"] == True:
            if source_framerate not in config["filters"]["framerate_whitelist"]:

                logger.warning(
                    f"[magenta]Media Pool Item: {mpi_uuid}[/]\n"
                    + f"[yellow]Ignoring non-whitelisted framerate: '{source_framerate}'[/] "
                    + f"from '{source_metadata['File Path']}' [/]\n",
                    extra={"markup": True},
                )
                continue

        # TODO: Add the Resolve API media pool item object so we can call it directly to link
        # source_metadata.update({'media_pool_item_object':media_pool_item})
        filtered_metadata.append(source_metadata)

    print(f"[green]Total queuable clips on timeline: {len(filtered_metadata)}[/]")

    return filtered_metadata
