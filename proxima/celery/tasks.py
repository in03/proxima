import logging
import os
from dataclasses import dataclass, fields

from celery.exceptions import Reject
from rich import print
from rich.console import Console

from proxima.app import core
from proxima.celery import celery_app
from proxima.celery.celery import celery_queue
from proxima.celery.ffmpeg import FfmpegProcess
from proxima.settings.manager import (
    App,
    BaseModel,
    Broker,
    Filters,
    Paths,
    Proxy,
    Settings,
    Worker,
    settings,
)
from proxima.types.job import ProjectMetadata, SourceMetadata

# Worker and Celery settings pulled from worker's proxima configuration.
# All other settings are passed from queuer
console = Console()

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")
logger.setLevel(settings.worker.loglevel)


def class_from_args(class_name, arg_dict: dict):
    fieldSet = {f.name for f in fields(class_name) if f.init}
    filteredArgDict = {k: v for k, v in arg_dict.items() if k in fieldSet}
    return class_name(**filteredArgDict)


class TaskSettings(BaseModel):
    app: App
    broker: Broker
    paths: Paths
    filters: Filters
    proxy: Proxy
    worker: Worker


@dataclass(frozen=True, init=True)
class TaskJob:
    settings: TaskSettings
    project: ProjectMetadata
    source: SourceMetadata

    output_file_path: str
    output_file_name: str
    output_directory: str
    input_level: str

    def __post_init__(self):
        # TODO: Custom exceptions for task job validation

        if not os.path.exists(self.source.file_path):  # SOURCE ACCESSIBLE
            raise FileNotFoundError(
                f"Provided source file '{self.source.file_path}' does not exist"
            )

        if os.path.exists(self.output_file_path):  # NO OVERWRITE
            raise FileExistsError(
                f"File already exists at provided output path {self.output_file_path}"
            )
        if self.input_level not in [
            "in_range=full",
            "in_range=limited",
        ]:  # CHECK VALID VIDEO LEVELS
            raise ValueError(
                f"Calculated video levels are invalid: '{self.input_level}'"
            )


def ffmpeg_video_flip(job: TaskJob):
    flip_string = ""
    if job.source.h_flip:
        flip_string += "hflip, "
    if job.source.v_flip:
        flip_string += "vflip, "
    return flip_string


@celery_app.task(
    bind=True,
    acks_late=True,
    track_started=True,
    prefetch_limit=1,
    soft_time_limit=60,
    reject_on_worker_lost=True,
    queue=celery_queue,
)
def encode_proxy(self, job_dict: dict) -> str:
    """
    Celery task to encode proxy media using parameters in job argument
    and user-defined settings
    """

    logger.debug(f"[magenta]Received job dict {job_dict}")

    project_metadata = class_from_args(ProjectMetadata, job_dict["project"])
    source_metadata = class_from_args(SourceMetadata, job_dict["source"])

    job = TaskJob(
        settings=TaskSettings(**job_dict["settings"]),
        project=project_metadata,
        source=source_metadata,
        output_file_path=job_dict["job"]["output_file_path"],
        output_file_name=job_dict["job"]["output_file_name"],
        output_directory=job_dict["job"]["output_directory"],
        input_level=job_dict["job"]["input_level"],
    )

    # Create proxy output directory
    os.makedirs(job.output_directory, exist_ok=True)

    # Print new job header ############################################

    print("\n")
    console.rule("[green]Received proxy encode job :clapper:[/]", align="left")
    print("\n")

    logger.info(
        f"[magenta bold]Job: [/]{self.request.id}\n"
        f"Input File: '{job.source.file_path}'"
    )

    ###################################################################

    # Log job details
    logger.info(f"Output File: '{job.output_file_path}'\n")
    logger.info(
        f"Source Resolution: {job.source.resolution[0]} x {job.source.resolution[1]}"
    )
    logger.info(
        f"Horizontal Flip: {job.source.h_flip}\n" f"Vertical Flip: {job.source.v_flip}"
    )
    logger.info(f"Starting Timecode: {job.source.start_tc}")

    # Get FFmpeg Command
    ps = job.settings.proxy

    ffmpeg_command = [
        # INPUT
        "ffmpeg",
        "-y",  # Never prompt!
        *ps.misc_args,
        "-i",
        job.source.file_path,
        # VIDEO
        "-c:v",
        ps.codec,
        "-profile:v",
        ps.profile,
        "-vsync",
        "-1",  # Necessary to match VFR
        # TODO: Format this better
        # It's hard to format this. Every arg behind the -vf flag
        # should be separated by a literal comma and NO SPACES to string them together as per ffmpeg syntax.
        # Any optional args must provide their own literal commas so as not to leave them stray
        # if disabled... Inline functions here are also confusing and "magical".
        # But we don't want to run them queuer side, only on final queueables.
        # labels: enhancement
        # VIDEO FILTERS
        "-vf",
        f"scale=-2:{ps.vertical_res},"
        f"scale={job.input_level}:out_range=limited, "
        f"{ffmpeg_video_flip(job)}"
        f"format={ps.pix_fmt}"
        if ps.pix_fmt
        else "",
        # AUDIO
        "-c:a",
        ps.audio_codec,
        "-ar",
        ps.audio_samplerate,
        # TIMECODE
        "-timecode",
        job.source.start_tc,
        # FLAGS
        "-movflags",
        "+write_colr",
        # OUTPUT
        job.output_file_path,
    ]

    print()  # Newline
    logger.debug(f"[magenta]Running! FFmpeg command:[/]\n{' '.join(ffmpeg_command)}\n")

    try:
        process = FfmpegProcess(
            task_id=self.request.id,
            channel_id=self.request.group,
            command=[*ffmpeg_command],
            ffmpeg_loglevel=ps.ffmpeg_loglevel,
        )
    except Exception as e:
        logger.error(f"[red]Error: {e}\nRejecting task to prevent requeuing.")
        raise Reject(e, requeue=False)

    # Create logfile
    encode_log_dir = job.settings.paths.ffmpeg_logfile_dir
    os.makedirs(encode_log_dir, exist_ok=True)
    logfile_path = os.path.normpath(
        os.path.join(encode_log_dir, job.output_file_name + ".txt")
    )
    logger.debug(f"[magenta]Encoder logfile path: {logfile_path}[/]")

    # Run encode job
    logger.info("[yellow]Encoding...[/]")

    try:
        process.run(self, logfile=logfile_path)

    except Exception as e:
        logger.exception(f"[red] :warning: Couldn't encode proxy.[/]\n{e}")

    return f"{job.source.file_name} encoded successfully"
