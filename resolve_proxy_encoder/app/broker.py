import logging
import json
import redis
import time
from rich.console import Console, Group
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.live import Live
from rich import print

from resolve_proxy_encoder.settings.manager import SettingsManager


class PubSub:
    def __init__(self, settings):
        """
        Initialise Redis connection

        Args:
            settings (SettingsManager instance)
        """

        broker_url = str(settings["broker"]["url"])
        self._host = str(broker_url.split("redis://")[1].split(":")[0])
        self._port = int(broker_url.split(":")[2].split("/")[0])
        self._db = int(broker_url[-1::])

        self.redis = redis.Redis(
            host=self._host, port=self._port, db=self._db, decode_responses=True
        )
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

    def publish(self, channel_pattern, **kwargs):

        self.redis.publish(
            channel_pattern,
            json.dumps(kwargs),
        )

    def subscribe(self, channel_pattern, handler):

        self.pubsub.psubscribe(**{f"{channel_pattern}*": handler})
        return self.pubsub


class ProgressTracker:
    def __init__(self, settings: SettingsManager, callable_tasks):
        """
        Track encoding progress of all tasks in a group

        `settings` needed for connection to broker
        `callable_tasks` needed to know task count
        for accurate progress bar rendering

        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(settings["app"]["loglevel"])

        self.redis = PubSub(settings)
        self.pubsub = self.redis.pubsub
        self.callable_tasks = callable_tasks

        self.matched_task_ids = []
        self.progress_vals = {}
        self.active_workers = []
        self.completed_tasks = 0
        self.group_id = None

    def _init_handlers(self):

        self.redis.subscribe("celery-task-meta", self.handle_task_event)
        self.redis.subscribe("task-progress", self.handle_task_progress)

    def _define_progress_bars(self):

        self.worker_spinner = Progress(
            SpinnerColumn(),
            # TODO: Get individual worker names instead of host machines
            # labels: enhancement
            TextColumn("[cyan]Using {task.fields[worker_count]} workers"),
        )

        self.average_progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[yellow]ETA:[/]"),
            TimeRemainingColumn(),
        )

        self.overall_progress = Progress(
            TextColumn("[cyan]{task.description}"),
            # TODO: Fix bar column not lining up with task_progress bars
            # Maybe we can make a spacer text column for all the bars and truncate long filenames with [...]?
            # labels: bug
            BarColumn(),
            TextColumn("[cyan]({task.completed} of {task.total})"),
        )

        # Create group of renderables
        self.progress_group = Group(
            self.worker_spinner,
            self.average_progress,
            self.overall_progress,
        )

    def _init_progress_bars(self):

        self.worker_id = self.worker_spinner.add_task(
            description="Active worker count", worker_count=0
        )

        self.average_id = self.average_progress.add_task(
            description="Average task progress",
            total=len(self.callable_tasks),
        )

        self.overall_id = self.overall_progress.add_task(
            description="Total task progress",
            total=len(self.callable_tasks),
        )

    def handle_task_event(self, message):

        data = json.loads(message["data"])

        # Is this one of our tasks, or another queuers?
        if self.group_id == data["group_id"]:
            self.matched_task_ids.append(data["task_id"])

            # Update discrete task progress
            if data["status"] in ["SUCCESS", "FAILURE"]:

                self.completed_tasks = self.completed_tasks + 1
                self.overall_progress.update(
                    task_id=self.overall_id,
                    completed=self.completed_tasks,
                    total=len(self.callable_tasks),
                )

            # Print task event updates
            worker = data["worker"]
            file_name = data["args"][0]["file_name"]

            switch = {
                "SUCCESS": f"[bold green] :green_circle: {worker}[/] -> finished '{file_name}'",
                "FAILURE": f"[bold red] :red_circle: {worker}[/] -> finished '{file_name}'",
                "STARTED": f"[bold cyan] :pinching_hand: {worker}[/] -> picked up '{file_name}'",
            }

            print(switch[data["status"]])

    def handle_task_progress(self, message):

        # If task is registered, track it
        data = json.loads(message["data"])
        if data["task_id"] in self.matched_task_ids:

            # Update progress for correct task
            self.progress_vals.update(
                {data["task_id"]: [data["completed"], data["total"]]}
            )
            self.logger.debug(f"Received progress update: {data['completed']}")
            self.logger.debug(f"Received progress update: {data['completed']}")

            # Get up-to-date average
            prog_list = list()
            for x in self.progress_vals.values():
                prog_list.append(x[1] / x[0])
            prog_sum = sum(prog_list)
            avg_progress = prog_sum / len(self.callable_tasks)

            # Log debug
            self.logger.debug(f"prog_list: {prog_list}")
            self.logger.debug(f"prog_sum: {prog_sum}")
            self.logger.debug(f"Current avg: {avg_progress}")

            # Update average progress bar
            self.average_progress.update(
                task_id=self.average_id,
                completed=avg_progress,
            )

            # Add new workers
            if data["worker_name"] not in self.active_workers:
                self.active_workers.append(data["worker_name"])

                # Update worker spinner
                self.worker_spinner.update(
                    task_id=self.worker_id,
                    worker_count=len(self.active_workers),
                )

    def report_progress(self, results, loop_delay=1, timeout=0.05):

        # I figure timeout should be shorter than loop delay,
        # that way we know we're not outpacing ourselves

        self.group_id = results.id

        self._define_progress_bars()
        self._init_progress_bars()
        self._init_handlers()

        with Live(self.progress_group):

            while not results.ready():

                # Handlers will be called implicitly
                # get_message itself will always return None
                _ = self.pubsub.get_message(timeout=timeout)

                # Let's be nice to the server ;)
                time.sleep(loop_delay)

            # Hide the progress bars after finish
            self.worker_spinner.update(task_id=self.worker_id, visible=False)
            # self.average_progress.update(task_id=self.average_id, visible=False)
            # self.overall_progress.update(task_id=self.overall_id, visible=False)

        return results
