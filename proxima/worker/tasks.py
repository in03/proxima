import logging

from proxima import core
from proxima.settings import SettingsManager
from proxima.worker import celery_app
from proxima.worker.ffmpeg import FfmpegProcess
from proxima.worker import utils
from celery.exceptions import Reject

from rich import print
from rich.console import Console

# Worker and Celery settings pulled from local user_settings file
# All other settings are passed from queuer
settings = SettingsManager()
console = Console()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["worker"]["loglevel"])


@celery_app.task(
    bind=True,
    acks_late=True,
    track_started=True,
    prefetch_limit=1,
    soft_time_limit=60,
    reject_on_worker_lost=True,
    queue=utils.get_queue(),
)
def encode_proxy(self, job):

    """
    Celery task to encode proxy media using parameters in job argument
    and user-defined settings
    """

    # Print new job header #####################################################################

    print("\n")
    console.rule(f"[green]Received proxy encode job :clapper:[/]", align="left")
    print("\n")

    logger.info(
        f"[magenta bold]Job: [/]{self.request.id}\n" f"Input File: '{job['file_path']}'"
    )

    ############################################################################################

    # Get proxy output path
    output_path = utils.ensure_output_paths(job)

    # Log job details
    logger.info(f"Output File: '{output_path}'\n")
    logger.info(
        f"Source Resolution: {int(job['resolution'][0])} x {int(job['resolution'][1])}"
    )
    logger.info(f"Horizontal Flip: {job['h_flip']}\n" f"Vertical Flip: {job['h_flip']}")
    logger.info(f"Starting Timecode: {job['start_tc']}")

    # Get FFmpeg Command
    ps = job["proxy_settings"]

    ffmpeg_command = [
        # INPUT
        "ffmpeg",
        "-y",  # Never prompt!
        *ps["misc_args"],
        "-i",
        job["file_path"],
        # VIDEO
        "-c:v",
        ps["codec"],
        "-profile:v",
        ps["profile"],
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
        f"scale=-2:{int(job['proxy_settings']['vertical_res'])},"
        f"scale={utils.get_input_level(job)}:out_range=limited, "
        f"{utils.get_flip(job)}"
        f"format={ps['pix_fmt']}"
        if ps["pix_fmt"]
        else "",
        # AUDIO
        "-c:a",
        ps["audio_codec"],
        "-ar",
        ps["audio_samplerate"],
        # TIMECODE
        "-timecode",
        job["start_tc"],
        # FLAGS
        "-movflags",
        "+write_colr",
        # OUTPUT
        output_path,
    ]

    print()  # Newline
    logger.debug(f"[magenta]Running! FFmpeg command:[/]\n{' '.join(ffmpeg_command)}\n")

    try:
        process = FfmpegProcess(
            task_id=self.request.id,
            channel_id=self.request.group,
            command=[*ffmpeg_command],
            ffmpeg_loglevel=ps["ffmpeg_loglevel"],
        )
    except Exception as e:
        logger.error(f"[red]Error: {e}\nRejecting task to prevent requeuing.")
        raise Reject(e, requeue=False)

    # Get logfile path
    logfile_path = utils.ensure_logs_output_path(job, output_path)
    logger.debug(f"[magenta]Encoder logfile path: {logfile_path}[/]")

    # Run encode job
    logger.info("[yellow]Encoding...[/]")

    try:
        process.run(self, logfile=logfile_path)

    except Exception as e:
        logger.exception(f"[red] :warning: Couldn't encode proxy.[/]\n{e}")

    return f"{job['file_name']} encoded successfully"
