import json
import logging
import os
import subprocess

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.prompt import Confirm

from proxima.app import core
from proxima.settings.manager import settings

from .utils import ffprobe

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")
logger.setLevel(settings.worker.loglevel)


class FfmpegProcess:
    def __init__(
        self, task_id: str, channel_id: str, command, ffmpeg_loglevel="verbose"
    ):
        """
        Creates the list of FFmpeg arguments.
        Accepts an optional ffmpeg_loglevel parameter to set the value of FFmpeg's -loglevel argument.
        """

        self.task_id = task_id
        self.channel_id = channel_id

        index_of_filepath = command.index("-i") + 1
        self._filepath = command[index_of_filepath]
        self._output_filepath = command[-1]

        dirname = os.path.dirname(self._output_filepath)

        if dirname != "":
            self._dir_files = [file for file in os.listdir(dirname)]
        else:
            self._dir_files = [file for file in os.listdir()]

        self._duration_seconds = float(ffprobe(self._filepath)["format"]["duration"])

        self._ffmpeg_args = command + ["-loglevel", ffmpeg_loglevel]
        self._ffmpeg_args += ["-progress", "pipe:1", "-nostats"]

    def run(self, celery_task_object, logfile=None):
        # Get progress bar
        console = Console(record=True)
        progress_bar = Progress(
            TextColumn("                   "),  # Spacer to match logging
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            # TextColumn("[progress.completed]{task.completed:>3.0f} of"),
            # TextColumn("[progress.total]{task.total:>3.0f} secs"),
            TextColumn("[yellow]ETA:[/]"),
            TimeRemainingColumn(),
            # TimeElapsedColumn(),
            console=console,
            transient=True,
        )

        # Open the logfile for logging if enabled
        if logfile:
            with open(logfile, "w") as f:
                pass

        # Catch the ffmpeg overwrite prompt
        if "-y" not in self._ffmpeg_args and self._output_filepath in self._dir_files:
            if not Confirm.ask(
                f"[yellow]'{self._output_filepath}' already exists. Overwrite?[/]"
            ):
                core.app_exit(0)

        self._ffmpeg_args += ["-y"]

        process = None

        if logfile:
            with open(logfile, "a") as f:
                process = subprocess.Popen(
                    self._ffmpeg_args, stdout=subprocess.PIPE, stderr=f
                )

        previous_seconds_processed = 0
        seconds_processed = 0

        encoding_task = progress_bar.add_task(
            description="[yellow]Encode[/]",
            total=self._duration_seconds,
        )

        # Don't continue if we don't have the process
        if not process:
            logger.critical("Couldn't start ffmpeg process!")
            core.app_exit(1, -1)

        try:
            progress_bar.start()

            while process.poll() is None:
                while not progress_bar.finished:
                    if not process.stdout:
                        break

                    ffmpeg_output = process.stdout.readline().decode()

                    if "out_time_ms" in ffmpeg_output:
                        seconds_processed = int(ffmpeg_output.strip()[12:]) / 1_000_000
                        seconds_increase = (
                            seconds_processed - previous_seconds_processed
                        )

                        # Update worker stdout progress bar
                        progress_bar.update(
                            task_id=encoding_task,
                            advance=seconds_increase,
                        )

                        # Update task custom state
                        celery_task_object.update_state(
                            state="ENCODING",
                            meta={
                                "percent": seconds_processed
                                / self._duration_seconds
                                * 100
                            },
                        )

                        previous_seconds_processed = seconds_processed

                    else:
                        break

            progress_bar.stop()
            logger.info("[green]Finished encoding[/]")

        except KeyboardInterrupt:
            progress_bar.stop()
            process.kill()
            print("[yellow][KeyboardInterrupt] FFmpeg process killed. Exiting...[/]")
            core.app_exit(0)

        except Exception as e:
            progress_bar.stop()
            process.kill()
            logger.critical(f"[red][Error] {e}\nExiting...[/]")
            core.app_exit(1, -1)
