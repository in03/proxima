import logging
import os
import pathlib
import re
from dataclasses import dataclass
from functools import cached_property
from glob import glob

from proxima.app import core, exceptions
from proxima.celery import ffmpeg
from proxima.settings.manager import Settings, settings
from proxima.types.media_pool_index import media_pool_index

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")
logger.setLevel(settings.app.loglevel)


@dataclass(frozen=True)
class SourceMetadata:
    clip_name: str
    file_name: str
    file_path: str
    duration: str
    resolution: list[int]
    data_level: str
    frames: int
    fps: float
    h_flip: bool
    v_flip: bool
    start: int
    end: int
    start_tc: str
    proxy_status: str
    proxy_media_path: str
    end_tc: str
    media_pool_id: str


@dataclass(frozen=True)
class ProjectMetadata:
    project_name: str
    timeline_name: str


@dataclass(init=True, repr=True)
class Job:
    def __init__(
        self,
        project_metadata: ProjectMetadata,
        source_metadata: SourceMetadata,
        settings: Settings,
    ):
        # Get data
        self.source = source_metadata
        self.project = project_metadata
        self.settings = settings

        # Dynamic values
        self.proxy_offline_status: bool = (
            True if self.source.proxy_status == "Offline" else False
        )

    def __repr__(self):
        status = "linked" if self.is_linked and not self.is_offline else "unlinked"
        status = "OFFLINE" if self.is_offline else status
        return f"Job object: '{self.source.file_name}' - {status} - {self.output_file_path}"

    @cached_property
    def output_file_path(self) -> str:
        """
        Get the determined output file path

        Derived from source structure.
        Collision free path calculated if overwrite mode is disabled.
        Cached to prevent recalculating each call.

        Returns:
            str: output_file_path
        """

        logger.info("[cyan]Getting collision-free path...")

        def get_collision_free_path(
            initial_output_path: str, increment_num: int = 1
        ) -> str:
            """Get a collision-free output path by incrementing the filename if it already exists"""

            while True:
                file_name, file_ext = os.path.splitext(initial_output_path)
                try_path = f"{file_name}_{increment_num}{file_ext}"

                if os.path.exists(try_path):
                    logger.debug(
                        f"[magenta] * Path '{os.path.basename(try_path)}' exists. Incrementing."
                    )
                    increment_num += 1

                else:
                    logger.debug(
                        f"[magenta] * Path '{os.path.basename(try_path)}' is free."
                    )
                    break

            return str(try_path)

        initial_output_path = os.path.join(self.output_directory, self.source.file_name)

        if self.settings.proxy.overwrite:
            if not os.path.exists(initial_output_path):
                return initial_output_path

            collision_free_path = get_collision_free_path(initial_output_path)
            logger.debug(
                f"[magenta] * Collision free path: '{core.shorten_long_path(collision_free_path)}'"
            )
            assert not os.path.exists(collision_free_path)
            return collision_free_path

        else:
            logger.debug(
                f"[magenta] * Output path, will overwrite existing: {initial_output_path}"
            )
            return initial_output_path

    @property
    def output_file_name(self) -> str:
        """
        Output file name without extension

        Returns:
            str: The file name without extension
        """
        return os.path.splitext(os.path.basename(self.output_file_path))[0]

    @property
    def output_directory(self):
        """Get output proxy dir, mirroring source subfolder structure"""
        file_path = self.source.file_path
        assert file_path
        p = pathlib.Path(file_path)

        return os.path.normpath(
            os.path.join(
                self.settings.paths.proxy_root,
                os.path.dirname(p.relative_to(*p.parts[:1])),
            )
        )

    @property
    def is_linked(self) -> bool:
        """Job with linked media that may or may not be \"Offline\" """

        if self.source.proxy_status == "None":
            return False
        return True

    @property
    def is_offline(self) -> bool:
        """Job with \"Offline\" linked media"""
        return self.proxy_offline_status

    @is_offline.setter
    def is_offline(self, value: bool):
        """Offline proxy media status setter"""

        assert isinstance(value, bool)
        self.managed_proxy_status = value
        return self.managed_proxy_status

    @cached_property
    def newest_linkable_proxy(self) -> str | None:
        """
        Return the newest linkable proxy for the current Job if any

        Uses `linkable_proxy_suffix_regex` user setting to filter
        allowable file suffixes.
        """

        logger.info("[cyan]Getting newest linkable proxy...")

        # Get glob path
        glob_path = os.path.splitext(
            os.path.join(
                self.output_directory,
                self.source.file_name,
            )
        )[0]

        # Fetch paths of all possible variants of source filename
        matches = glob(glob_path + "*.*")

        candidates = []
        for x in matches:
            # If exact match
            if os.path.basename(x).upper() == self.source.file_name.upper():
                logger.debug(f"[magenta] * Found exact match: '{os.path.basename(x)}'")
                candidates.append(x)
                continue

            # If match allowed suffix
            basename = os.path.basename(x)
            candidate_filename = os.path.splitext(basename)[0]
            for criteria in self.settings.paths.linkable_proxy_suffix_regex:
                logger.debug(
                    f"[magenta] * Search regex '{criteria}' in filename '{candidate_filename}' "
                )
                if re.search(criteria, candidate_filename):
                    logger.debug(
                        f"[green]   * Found regex criteria match: '{os.path.basename(x)}'"
                    )
                    candidates.append(x)
                    continue

                else:
                    logger.debug("[yellow]   * Not found")

        if not candidates:
            return None

        if len(candidates) == 1:
            return os.path.normpath(candidates[0])

        candidates = sorted(candidates, key=os.path.getmtime, reverse=True)
        logger.debug(f"[magenta] * Newest match: '{os.path.basename(candidates[0])}'")
        return os.path.normpath(candidates[0])

    @cached_property
    def input_level(self) -> str:
        """
        Match Resolve's set data levels ("Auto", "Full" or "Video")

        Uses ffprobe to probe file for levels if Resolve data levels are set to Auto.
        """

        logger.info("[cyan]Getting input level...")

        def probe_for_input_range(self):
            """
            Probe file with ffprobe for colour range
            and map to ffmpeg 'in_range' value ("full" or "limited")
            """

            input = self.source.file_path
            streams = ffmpeg.ffprobe(file=input)["streams"]

            # Get first valid video stream
            video_info = None
            for stream in streams:
                logger.debug(
                    f"[magenta] * Found stream '{stream.get('codec_long_name', 'Data stream')}'"
                )
                if stream["codec_type"] == "video":
                    if stream["r_frame_rate"] != "0/0":
                        video_info = stream
            assert video_info is not None

            color_data = {k: v for k, v in video_info.items() if "color" in k}
            logger.debug(f"[magenta] * Color data: {color_data}")

            if "color_range" in color_data.keys():
                switch = {
                    "pc": "in_range=full",
                    "tv": "in_range=limited",
                }
                return switch[video_info["color_range"]]

            else:
                logger.warning(
                    f"[yellow]Couldn't get color range metadata from file {self.source.file_name}! Assuming 'limited'..."
                    "If interpretation is inaccurate, please transcode to a format that supports color metadata."
                )
                return "in_range=limited"

        switch = {
            "Auto": probe_for_input_range(self),
            "Full": "in_range=full",
            "Video": "in_range=limited",
        }

        return switch[self.source.data_level]

    def link_proxy(self, proxy_media_path: str):
        """
        Wrapper around Resolve's `LinkProxyMedia` API method.

        Args:
            job (): A Proxima Job

        Raises:
            FileNotFoundError: Occurs when the proxy media file does not exist at `proxy_media_path`.

            exceptions.ResolveLinkMismatchError: Occurs when the method returns False.
            Unfortunately the method returns no error context beyond that.
        """

        media_pool_item = media_pool_index.lookup(self.source.media_pool_id)
        logger.debug(
            f"[magenta]Attempting to link:[/]\n - PROXY: '{proxy_media_path}'\n - SOURCE: '{self.source.file_path}'"
        )

        if not os.path.exists(proxy_media_path):
            raise FileNotFoundError(
                f"Proxy media file does not exist at path: '{proxy_media_path}'"
            )

        if not media_pool_item.link_proxy(proxy_media_path):
            raise exceptions.ResolveLinkMismatchError(proxy_file=proxy_media_path)
