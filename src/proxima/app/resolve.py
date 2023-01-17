import logging
import os

from proxima.app import core
from proxima.settings import settings, SettingsManager
from pydavinci import davinci
from pydavinci.wrappers.timeline import Timeline
from pydavinci.wrappers.project import Project
from pydavinci.wrappers.timelineitem import TimelineItem
from pydavinci.wrappers.mediapool import MediaPool
from pydavinci.wrappers.mediapoolitem import MediaPoolItem
from proxima.types.media_pool_index import media_pool_index
from proxima.types.job import Job, ProjectMetadata, SourceMetadata
from proxima.types.batch import Batch

resolve = davinci.Resolve()

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")
logger.setLevel(settings["app"]["loglevel"])


def get_timeline_items(timeline: Timeline) -> list[TimelineItem]:
    """
    Get all video track items from the provided timeline

    Args:
        timeline (Timeline): Provided DaVinci Resolve timeline object

    Returns:
        list[TimelineItem]: List of Davinci Resolve timelineitems.
    """

    logger.info("[cyan]Getting timeline items...")

    all_track_items = []

    track_len = timeline.track_count("video")
    logger.debug(f"[magenta] * Video tracks: {track_len}[/]")
    for i in range(1, track_len + 1):

        # Get items
        all_track_items.extend(timeline.items("video", i))

    return all_track_items


def get_media_pool_items(timeline_items: list[TimelineItem]) -> list[MediaPoolItem]:
    """
    Get media pool items from timeline items.

    Args:
        timeline_items (list[TimelineItem]): List of timeline items.

    Returns:
        list[MediaPoolItem]|None: List of media pool items.
    """

    media_pool_items = []
    already_seen = []

    logger.info("[cyan]Getting media pool items...")

    for item in timeline_items:

        # Bit weird, but items without mediapoolitems still have the attribute
        # and accessing it at all causes a TypeError.
        try:
            item.mediapoolitem
        except TypeError:
            logger.debug(f"[magenta] * Ignoring '{item.name}' without mediapoolitem")
            continue

        if item.mediapoolitem.media_id in already_seen:
            logger.debug(
                f"[magenta] * Ignoring duplicate item '{item.mediapoolitem.media_id}'"
            )
            continue

        media_pool_items.append(item.mediapoolitem)
        already_seen.append(item.mediapoolitem.media_id)

    return media_pool_items


def get_resolve_timelines(
    project: Project,
) -> list[Timeline] | None:
    """
    Return a list of all Resolve timeline objects in current project.

    Args:
        project (Project): DaVinci Resolve Project object

    Returns:
        list[Timeline]|None: List of DaVinci Resolve timeline objects. None if none found.
    """

    logger.debug("[cyan]Getting Resolve timelines...")

    timelines = project.timelines
    if not timelines:
        return None

    # Make active timeline first in list
    timeline_names = [x.name for x in timelines]
    active_index = timeline_names.index(project.timeline.name)
    timelines.insert(0, timelines.pop(active_index))

    return timelines


def filter_queueable(media_pool_items: list[MediaPoolItem]) -> list[MediaPoolItem]:

    logger.debug("[magenta] * Filtering queueable jobs...")

    seen = []

    if not media_pool_items:
        raise ValueError("No media pool items were passed")

    for mpi in media_pool_items:
        if mpi.media_id in seen:
            logger.debug(
                f"[cyan]Media Pool Item: '{mpi.media_id}' alreeady seen, skipping...\n"
            )
            continue
        seen.append(mpi.media_id)

        if not hasattr(mpi, "properties"):
            logger.debug(
                f"[magenta] * Media Pool Item: {mpi.media_id}[/]\n"
                + "[yellow]Media pool item has no clip properties. Skipping...[/]\n"
            )
            continue

        # Filepath won't exist for internally generated media
        source_path = mpi.properties["File Path"]  # type: ignore
        if not source_path:
            continue

        source_ext = os.path.splitext(source_path)[1].lower()

        # Filter extension
        if settings["filters"]["extension_whitelist"]:

            if source_ext not in settings["filters"]["extension_whitelist"]:

                logger.warning(
                    f"[yellow]Ignoring file with extension not in whitelist: '{source_ext}'\n"
                    + f"from '{mpi.properties['File Path']}'[/]\n"
                )
                continue

        # Filter framerate
        if settings["filters"]["framerate_whitelist"]:

            # Make int to avoid awkward extra zeros.
            if float(mpi.properties["FPS"]).is_integer():
                mpi.properties["FPS"] = int(float(mpi.properties["FPS"]))

            if mpi.properties["FPS"] not in settings["filters"]["framerate_whitelist"]:

                logger.warning(
                    f"[yellow]Ignoring file with framerate not in whitelist: '{mpi.properties['FPS']}'\n"
                    + f"from '{mpi.properties['File Path']}' [/]\n"
                )
                continue

    return media_pool_items


def generate_batch(
    media_pool_items: list[MediaPoolItem], settings: SettingsManager
) -> Batch:

    logger.info("[cyan]Generating batch of jobs...")

    job_list = []
    for mpi in media_pool_items:

        global media_pool_index

        props = mpi.properties
        project_metadata = ProjectMetadata(
            resolve.project.name, resolve.active_timeline.name
        )

        source_metadata = SourceMetadata(
            clip_name=props["Clip Name"],
            file_name=props["File Name"],
            file_path=props["File Path"],
            duration=props["Duration"],
            resolution=[int(x) for x in str(props["Resolution"]).split("x")],
            data_level=props["Data Level"],
            frames=int(props["Frames"]),
            fps=float(props["FPS"]),
            h_flip=True if props["H-FLIP"] == "On" else False,
            v_flip=True if props["H-FLIP"] == "On" else False,
            start=int(props["Start"]),
            end=int(props["End"]),
            start_tc=props["Start TC"],
            end_tc=props["End TC"],
            proxy_status=props["Proxy"],
            proxy_media_path=props["Proxy Media Path"],
            media_pool_id=mpi.media_id,
        )

        job_list.append(Job(project_metadata, source_metadata, settings))
        media_pool_index.add_to_index(mpi)

    jobs = Batch(job_list)
    return jobs
