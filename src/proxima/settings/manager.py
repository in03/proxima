from __future__ import annotations

import logging
import os
import pathlib
import re

import rich.traceback
import rtoml
from pydantic import (
    BaseModel,
    BaseSettings,
    Field,
    RedisDsn,
    ValidationError,
    validator,
)
from pydantic.env_settings import SettingsSourceCallable
from rich import print
from rich.panel import Panel

from proxima.app.core import setup_rich_logging
from proxima.settings import dotenv_settings_file, user_settings_file

setup_rich_logging()

logger = logging.getLogger("proxima")
rich.traceback.install(show_locals=False)


def load_toml_user(_):
    user_toml = pathlib.Path(user_settings_file)
    return rtoml.load(user_toml.read_text())


class App(BaseModel):
    loglevel: str = Field("WARNING", description="General application loglevel")
    check_for_updates: bool = Field(
        True, description="Enable/Disable checking for updates"
    )
    version_constrain: bool = Field(
        False,
        description="Enable/disable version constrained queuer/worker compatibility. Keep it enabled unless you're sure!",
    )

    @validator("loglevel")
    def must_be_valid_loglevel(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(
                f"'{v}' is not a valid loglevel. Choose from [cyan]{', '.join(valid_levels)}[/]"
            )
        return v


class Paths(BaseModel):
    proxy_root: str = Field(
        ..., description="Root directory for proxy transcode structure"
    )
    ffmpeg_logfile_dir: str = Field(..., description="Path for ffmpeg logfiles")
    linkable_proxy_suffix_regex: list[str] = Field(..., min_items=1, unique_items=True)

    @validator("proxy_root", "ffmpeg_logfile_dir")
    def check_path_exists(cls, v):
        if not os.path.exists(v):
            raise ValueError(f"Path {v} does not exist")
        return v

    @validator("linkable_proxy_suffix_regex", each_item=True)
    def must_be_valid_regex(cls, v):
        try:
            re.compile(v)
        except Exception:
            raise ValueError(f"Invalid regex for setting {v}")
        return v


class Proxy(BaseModel):
    ffmpeg_loglevel: str = Field(
        ..., description="Ffmpeg's internal loglevel visible in worker output"
    )
    nickname: str = Field(
        ..., description="Encoding preset nickname for easy reference"
    )
    codec: str = Field(..., description="Ffmpeg supported codec for proxy transcoding")
    vertical_res: str = Field(
        ...,
        description="Target vertical resolution in pixels (aspect ratio is automatically preserved)",
    )
    profile: str = Field(..., description="Ffmpeg profile for given codec")
    pix_fmt: str = Field(..., description="Ffmpeg pixel format for given codec")
    audio_codec: str = Field(
        ...,
        description="Ffmpeg supported audio codec for given format/container",
    )
    audio_samplerate: str = Field(
        ...,
        description="Ffmpeg supported audio samplerate for audio codec",
    )
    misc_args: list[str] = Field(..., description="Misc Ffmpeg starting arguments")
    ext: str = Field(
        ...,
        description="Extension for Ffmpeg supported container (must be compatible with other proxy settings!)",
    )
    overwrite: bool = Field(
        ...,
        description="Whether or not to overwrite any existing proxy files on collision",
    )


class Filters(BaseModel):
    extension_whitelist: list[str] = Field(
        ...,
        min_items=0,
        unique_items=True,
        description="Only transcode source media with these file extensions. Leave empty to disable.",
    )
    framerate_whitelist: list[int] = Field(
        ...,
        min_items=0,
        unique_items=True,
        description="Only transcode source media with these framerates. Leave empty to disable.",
    )

    @validator("extension_whitelist", each_item=True)
    def check_are_file_extensions(cls, v):
        if not v.startswith("."):
            raise ValueError(f"{v} is not a valid file extension")
        return v


class Broker(BaseModel):
    url: RedisDsn = Field(..., description="Redis broker address")
    job_expires: int = Field(
        ...,
        description="How long until a queued proxy job expires if not received by a worker. Default: 1 hr",
    )
    result_expires: int = Field(
        ...,
        description="How long until a proxy job's result is discared. Default: 1 day. Used by monitor webapp",
    )


class Worker(BaseModel):
    loglevel: str = Field(..., description="Worker loglevel")
    terminal_args: list[str] = Field(
        ...,
        min_items=0,
        description="Pre-command args. Use to invoke the command through another shell/terminal.",
    )
    celery_args: list[str] = Field(
        ...,
        min_items=0,
        description="Pre-command args. Use to invoke the command through another shell/terminal.",
    )

    @validator("loglevel")
    def must_be_valid_loglevel(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"{v} is not a valid loglevel. Choose from {valid_levels}")
        return v


class Settings(BaseSettings):
    app: App
    broker: Broker
    filters: Filters
    paths: Paths
    proxy: Proxy
    worker: Worker

    class Config:
        env_file = dotenv_settings_file
        env_file_encoding = "utf-8"
        env_prefix = "PROXIMA_"
        env_nested_delimiter = "__"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ) -> tuple[SettingsSourceCallable, ...]:
            return (
                env_settings,
                load_toml_user,
                file_secret_settings,
                init_settings,
            )


settings = None


try:
    settings = Settings()

except ValidationError as e:
    print(
        Panel(
            title="[red]Uh, oh! Invalid user settings",
            title_align="left",
            highlight=True,
            expand=False,
            renderable=f"\n{str(e)}\n\nRun 'Proxima config --help' to see how to fix broken settings.",
        )
    )

if __name__ == "__main__":
    if settings:
        print(settings.dict())
