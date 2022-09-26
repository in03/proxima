from typing import List
import logging
import time
from rich.console import Group
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.live import Live
from celery.result import AsyncResult

logger = logging.getLogger(__name__)


class ProgressTracker:
    def __init__(self):
        """
        Track encoding progress of all tasks in a group
        for accurate progress bar rendering
        """

        self.already_seen = {}

    def __define_progress_bars(self):

        self.status_view = Progress(
            TextColumn("{task.fields[last_status]}"),
        )

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[cyan][progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn(
                "[cyan]{task.fields[completed_tasks]}/{task.fields[total_tasks]} | "
                "{task.fields[active_workers]} workers"
            ),
        )

        # Create group of renderables
        self.progress_group = Group(
            self.status_view,
            "",  # This actually works as a spacer lol
            self.progress,
        )

    def __init_progress_bars(self):

        self.status_view_id = self.status_view.add_task(
            description="Last task event status",
            last_status="",
        )

        self.progress_id = self.progress.add_task(
            active_workers=0,
            description="Task progress",
            total=100,  # percentage
            completed_tasks=0,
            total_tasks=0,
        )

    def update_last_status(self, task_results: List[AsyncResult]):

        for result in task_results:

            if not result or not result.args:
                continue

            # Skip if we've already seen this data
            if (
                result.id in self.already_seen
                and self.already_seen[result.id] == result.status
            ):
                continue

            switch = {
                "STARTED": f"[bold cyan] :blue_circle: {result.worker}[/] -> [cyan]started on '{result.args[0]['file_name']}'",
                "SUCCESS": f"[bold green] :green_circle: {result.worker}[/] -> [green]finished '{result.args[0]['file_name']}'",
                "FAILURE": f"[bold red] :red_circle: {result.worker}[/] -> [red]failed '{result.args[0]['file_name']}'",
            }

            if last_status := switch.get(result.status):

                self.status_view.update(
                    task_id=self.status_view_id,
                    last_status=last_status,
                )

            # Add to already seen, so we don't handle this event again
            self.already_seen.update({result.id: result.status})

    def update_progress(self, task_results: List[AsyncResult]):

        # Get encoding progress from task custom status
        progress_data = [
            x.info["percent"] for x in task_results if x.status == "ENCODING"
        ]
        if not progress_data:
            return

        # Make sure we keep account for finished tasks
        completed_data = [100 for x in task_results if x.ready()]
        progress_data.extend(completed_data)
        progress_avg = sum(progress_data) / len(task_results)

        # Update average progress
        self.progress.update(
            task_id=self.progress_id,
            completed=progress_avg,
        )

        # try:
        #     progress_avg = sum(progress_data) / len(task_results)
        # except ZeroDivisionError:
        #     self.logger.debug(
        #         "[yellow]Encountered division by zero error! Setting progress to zero."
        #     )
        #     progress_avg = 0.0

    def report_progress(self, group_results):

        self.group_id = group_results.id
        self.__define_progress_bars()
        self.__init_progress_bars()

        with Live(self.progress_group):

            try:

                while not group_results.ready():

                    # UPDATE PROGRESS
                    task_results = group_results.results
                    self.update_progress(task_results)

                    # HANDLE LAST STATUS
                    self.update_last_status(task_results)

                    # HANDLE TASK INFO
                    self.progress.update(
                        task_id=self.progress_id,
                        active_workers=len(
                            [x for x in task_results if x.status == "ENCODING"]
                        ),
                        completed_tasks=group_results.completed_count(),
                        total_tasks=len(task_results),
                    )

                    time.sleep(0.001)

            except:
                raise

            finally:
                # Allow reading final results
                time.sleep(2)

            # Hide the progress bars after finish
            self.status_view.update(task_id=self.status_view_id, visible=False)
            self.progress.update(task_id=self.progress_id, visible=False)

        return group_results
