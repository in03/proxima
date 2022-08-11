from decimal import DivisionByZero
from typing import Union
import logging
import json
import redis
import time
from rich.console import Group
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.live import Live
from cryptohash import sha1

from resolve_proxy_encoder.settings.manager import SettingsManager


class RedisConnection:

    """
    Redis connection class.

    Pulls connection settings from config into new Redis connection instance.

    Attributes:
        connection (Redis, None): Connection object used to interface with Redis.
        settings (SettingsManager): Configuration used for connection.
    """

    def __init__(self, settings: SettingsManager):
        self.connection: Union[redis.Redis, None] = None
        self.settings = settings

    def get_connection(self):
        """
        Initialise Redis connection.

        Returns:
            connection(Redis, None): Connection object used to interface with Redis.
        """

        broker_url = str(self.settings["broker"]["url"])
        host = str(broker_url.split("redis://")[1].split(":")[0])
        port = int(broker_url.split(":")[2].split("/")[0])

        self.connection = redis.Redis(host=host, port=port, decode_responses=False)
        return self.connection


class ProgressTracker:
    def __init__(self, settings: SettingsManager, callable_tasks):
        """
        Track encoding progress of all tasks in a group

        `settings` needed for connection to broker
        `callable_tasks` needed to know task count
        for accurate progress bar rendering

        """

        redis = RedisConnection(settings)
        self.redis = redis.get_connection()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(settings["app"]["loglevel"])

        self.callable_tasks = callable_tasks

        self.matched_task_ids = []
        self.progress_latest_data = {}
        self.prog_percentages = {}
        self.last_task_average = 0

        self.active_workers = list()
        self.completed_tasks = 0
        self.group_id = None

        self.data_checksums = list()

    def __define_progress_bars(self):

        self.last_status = Progress(
            TextColumn("{task.fields[last_status]}"),
        )

        self.worker_spinner = Progress(
            SpinnerColumn(),
            # TODO: Get individual worker names instead of host machines
            # labels: enhancement
            TextColumn("[cyan]Using {task.fields[active_workers]} workers"),
        )

        self.average_progress = Progress(
            TextColumn("[cyan][progress.description]{task.description}"),
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
            self.last_status,
            "",  # This actually works as a spacer lol
            self.worker_spinner,
            self.average_progress,
            self.overall_progress,
        )

    def __init_progress_bars(self):

        self.worker_id = self.last_status.add_task(
            description="Last task event status",
            last_status="",
        )
        self.last_status_id = self.worker_spinner.add_task(
            description="Active worker count",
            active_workers=0,
            last_status="",
        )

        self.average_id = self.average_progress.add_task(
            description="Average task progress",
            total=100,  # percentage
        )

        self.overall_id = self.overall_progress.add_task(
            description="Total task progress",
            total=len(self.callable_tasks),
        )

    def get_new_data(self, key):

        data = self.redis.get(key)
        if data is None:
            self.logger.debug(f"[yellow]Could not get value from key: '{key}'")
            return None

        # TODO: This shouldn't be returning invalid JSON?
        # Not sure why but every 8th poll returns a value that isn't None, but isn't JSON.
        # Also, JSONDecodeError is actually thrown as ValueError. Which is weird
        # labels: Enhancement

        try:
            data = json.loads(data)
        except ValueError:
            self.logger.debug(f"[yellow]Could not decode value from key {key}")
            return None

        if not self.__data_is_new(data):
            self.logger.debug(
                f"Fetching redis key: '{key}' returned stale data:\n{data}"
            )
            return None

        return data

    def __data_is_new(self, data):

        checksum = sha1(str(data))

        if checksum in self.data_checksums:
            return False
        else:
            self.data_checksums.append(checksum)
            return True

    def handle_task_event(self, key):

        data = self.get_new_data(key)
        if data == None:
            return

        # Is this one of our tasks, or another queuers?
        if self.group_id == data["group_id"]:

            # Update worker count
            self.matched_task_ids.append(data["task_id"])
            if data["worker"] not in self.active_workers:
                self.active_workers.append(data["worker"])

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
                "FAILURE": f"[bold red] :red_circle: {worker}[/] -> [red]failed '{file_name}'",
                "STARTED": f"[bold cyan] :blue_circle: {worker}[/] -> picked up '{file_name}'",
            }

            self.status = switch[data["status"]]

            # Update spinner last status
            self.last_status.update(
                task_id=self.last_status_id,
                last_status=switch[data["status"]],
            )

            # Update worker spinner
            self.worker_spinner.update(
                task_id=self.worker_id,
                active_workers=len(self.active_workers),
            )

    def handle_task_progress(self, key):

        data = self.get_new_data(key)
        if not data:
            self.logger.debug(f"[magenta]Progress data: {data}")
            return

        # If task is registered, track it
        if data["task_id"] in self.matched_task_ids:

            # Store all vals for future purposes maybe?
            self.progress_latest_data.update(
                {data["task_id"]: [data.get("completed"), data.get("total")]}
            )
            # Get up-to-date average
            progress_data = self.progress_latest_data[data["task_id"]]
            percentage = round(progress_data[0] / progress_data[1] * 100)
            self.prog_percentages.update({data["task_id"]: percentage})
            active_task_average = round(
                sum(self.prog_percentages.values()) / len(self.prog_percentages)
            )
            try:
                total_task_average = round(
                    active_task_average
                    / (len(self.callable_tasks) - self.completed_tasks)
                )
            except DivisionByZero:
                total_task_average = 0

            # Log debug
            self.logger.debug(f"[magenta]Current task percentage: {percentage}")
            self.logger.debug(
                f"[magenta]Active tasks average percentage: {active_task_average}"
            )
            self.logger.debug(
                f"[magenta]Total tasks average percentage: {total_task_average}\n"
            )

            # TODO: Better way to prevent progress going backward on task pickup?
            # Not sure why the task progress is going backwards.
            # It happens on new task pick up, which I thought we accounted for?
            # It doesn't seem to be off by much though.
            # labels: enhancement
            if total_task_average > self.last_task_average:

                # Update average progress bar
                self.average_progress.update(
                    task_id=self.average_id,
                    completed=total_task_average,
                )

    def report_progress(self, results, loop_delay=1):

        # I figure timeout should be shorter than loop delay,
        # that way we know we're not outpacing ourselves

        self.group_id = results.id

        self.__define_progress_bars()
        self.__init_progress_bars()

        with Live(self.progress_group):

            while not results.ready():

                task_events = [
                    x
                    for x in self.redis.scan_iter("celery-task-meta*")
                    if x is not None
                ]
                progress_events = [
                    x for x in self.redis.scan_iter("task-progress*") if x is not None
                ]

                for te in task_events:
                    self.handle_task_event(te)

                for pe in progress_events:
                    self.handle_task_progress(pe)

                # Let's be nice to the server ;)
                time.sleep(loop_delay)

            # Hide the progress bars after finish
            self.worker_spinner.update(task_id=self.worker_id, visible=False)
            self.last_status.update(task_id=self.last_status_id, visible=False)
            self.average_progress.update(task_id=self.average_id, visible=False)
            self.overall_progress.update(task_id=self.overall_id, visible=False)

        return results
