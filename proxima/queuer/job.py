import logging
import os

from proxima import core, exceptions

import os
import pathlib
import re

from dataclasses import dataclass
from glob import glob
from functools import cached_property

from proxima.settings.manager import settings, SettingsManager

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


@dataclass(frozen=True)
class SourceMetadata:

    clip_name: str
    file_name: str
    file_path: str
    duration: str
    resolution: list
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
        file_name = self.source.file_name
        status = "linked" if self.is_linked and not self.is_offline else "unlinked"
        status = "OFFLINE" if self.is_offline else status
        output_path = self.output_path

        return f"Job object: '{file_name}' - {status} - {output_path}"

    @property
    def output_path(self):
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
        matches = glob.glob(glob_path + "*.*")

        candidates = []
        for x in matches:

            # If exact match
            if x == self.source.file_name:
                candidates.append(x)

            # If match allowed suffix
            basename = os.path.basename(x)
            candidate_suffix = basename.split(self.source.file_name)[1]
            for criteria in self.settings["paths"]["linkable_proxy_suffix_regex"]:
                if re.search(criteria, candidate_suffix):
                    candidates.append(x)

        if not candidates:
            return None

        if len(candidates) == 1:
            return os.path.normpath(candidates[0])

        candidates = sorted(candidates, key=os.path.getmtime, reverse=True)
        return os.path.normpath(candidates[0])

    @property
    def output_directory(self):
        """Get output proxy dir, mirroring source subfolder structure"""
        file_path = self.source.file_path
        p = pathlib.Path(file_path)

        return os.path.normpath(
            os.path.join(
                settings["paths"]["proxy_path_root"],
                os.path.dirname(p.relative_to(*p.parts[:1])),
            )
        )
