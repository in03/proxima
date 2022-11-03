import logging
import os

from proxima.app import core
from proxima.worker.ffmpeg import ffprobe

import os
import pathlib
import re

from dataclasses import dataclass
from glob import glob
from functools import cached_property

from proxima.settings import settings, SettingsManager

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


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


@dataclass(frozen=True)
class ProxySettings:
    ffmpeg_loglevel: list[str]
    codec: str
    vertical_res: str
    profile: str
    pix_fmt: str
    audio_codec: str
    audio_samplerate: str
    misc_args: list[str]
    ext: str


@dataclass(init=True, repr=True)
class Job:
    def __init__(
        self,
        project_metadata: ProjectMetadata,
        source_metadata: SourceMetadata,
        settings: SettingsManager,
    ):

        # Get data
        self.source = source_metadata
        self.project = project_metadata
        self.settings = settings

    def __repr__(self):
        status = "linked" if self.is_linked and not self.is_offline else "unlinked"
        status = "OFFLINE" if self.is_offline else status
        return f"Job object: '{self.source.file_name}' - {status} - {self.output_file_path}"

    @cached_property
    def output_file_path(self) -> str:
        """Get a clear output path for Job, incrementing if any exist"""

        def collision_free_path(
            initial_output_path: str, increment_num: int = 1
        ) -> str:
            """Get a collision-free output path by incrementing the filename if it already exists"""

            file_name, file_ext = os.path.splitext(initial_output_path)
            if os.path.exists(initial_output_path):

                if file_name.endswith(f"_{increment_num}"):

                    increment_num += 1
                    collision_free_path(initial_output_path, increment_num)

                file_name = file_name + "_1"

            return str(file_name + file_ext)

        initial_output_path = os.path.join(self.output_directory, self.source.file_name)
        return collision_free_path(initial_output_path)

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
                settings["paths"]["proxy_path_root"],
                os.path.dirname(p.relative_to(*p.parts[:1])),
            )
        )

    @property
    def is_linked(self) -> bool:
        """Whether or not the job has linked proxy media"""

        if self.source.proxy_status in ["None", "Offline"]:
            return False
        return True

    @property
    def is_offline(self) -> bool:
        """Whether or not the job has offline proxy media"""

        if self.source.proxy_status == "Offline":
            return True
        return False

    @cached_property
    def newest_linkable_proxy(self) -> str | None:
        """
        Return the newest linkable proxy for the current Job if any

        Uses `linkable_proxy_suffix_regex` user setting to filter
        allowable file suffixes.
        """

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
            if x == self.source.file_name:
                candidates.append(x)

            # If match allowed suffix
            basename = os.path.basename(x)
            candidate_suffix = os.path.splitext(basename)[1]
            for criteria in self.settings["paths"]["linkable_proxy_suffix_regex"]:
                if re.search(criteria, candidate_suffix):
                    candidates.append(x)

        if not candidates:
            return None

        if len(candidates) == 1:
            return os.path.normpath(candidates[0])

        candidates = sorted(candidates, key=os.path.getmtime, reverse=True)
        return os.path.normpath(candidates[0])

    @cached_property
    def input_level(self) -> str:
        """
        Match Resolve's set data levels ("Auto", "Full" or "Video")

        Uses ffprobe to probe file for levels if Resolve data levels are set to Auto.
        """

        def probe_for_input_range(self):
            """
            Probe file with ffprobe for colour range
            and map to ffmpeg 'in_range' value ("full" or "limited")
            """

            input = self.source.file_path
            streams = ffprobe(file=input)["streams"]

            # Get first valid video stream
            video_info = None
            for stream in streams:
                logger.debug(f"[magenta]Found stream {stream}")
                if stream["codec_type"] == "video":
                    if stream["r_frame_rate"] != "0/0":
                        video_info = stream
            assert video_info != None

            color_data = {k: v for k, v in video_info.items() if "color" in k}
            logger.debug(f"Color data:\n{color_data}")

            if "color_range" in color_data.keys():
                switch = {
                    "pc": "in_range=full",
                    "tv": "in_range=limited",
                }
                return switch[video_info["color_range"]]

            else:

                logger.warning(
                    "[yellow]Couldn't get color range metadata from file! Assuming 'limited'..."
                    "If interpretation is inaccurate, please transcode to a format that supports color metadata."
                )
                return "in_range=limited"

        switch = {
            "Auto": probe_for_input_range(self),
            "Full": "in_range=full",
            "Video": "in_range=limited",
        }

        return switch[self.source.data_level]
