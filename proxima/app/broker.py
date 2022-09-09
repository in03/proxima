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
)
from rich.live import Live
from proxima.settings import SettingsManager


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
        self.pubsub = self.redis.pubsub()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(settings["app"]["loglevel"])

        self.callable_tasks = callable_tasks

        self.new_task_data_exists = False
        self.new_progress_data_exists = False

        self.new_task_data = dict()
        self.prog_percentages = dict()
        self.active_workers = list()
        self.completed_tasks = int()
        self.group_id = None

    def __define_progress_bars(self):

        self.last_status = Progress(
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
            self.last_status,
            "",  # This actually works as a spacer lol
            self.progress,
        )

    def __init_progress_bars(self):

        self.last_status_id = self.last_status.add_task(
            description="Last task event status",
            last_status="",
        )

        self.progress_id = self.progress.add_task(
            active_workers=0,
            description="Task progress",
            total=100,  # percentage
            completed_tasks=0,
            total_tasks=len(self.callable_tasks),
        )

    def task_event_handler(self, message):

        assert message
        data = dict(**json.loads(message["data"]))
        self.logger.debug(f"[magenta]Received task event\n{data}")
        self.new_task_data_exists = True
        self.new_task_data = data

    def progress_event_handler(self, message):

        assert message
        data = dict(**json.loads(message["data"]))
        self.logger.debug(f"[magenta]Received progress event\n{data}")
        self.prog_percentages.update({data["task_id"]: data["percent"]})
        self.new_progress_data_exists = True

    def parse_task_info_data(self):
        """
        Parse task info data generated by `task_event_handler`

        Sets:
            - self.completed_tasks: the amount of fully completed tasks to date
            - self.active_workers: The amount of workers currently working on tasks in the group
            - self.last_status: The last worker event displayed like `worker_name: STARTED -> file_name`
        """
        assert self.new_task_data
        data = self.new_task_data

        # Is this one of our tasks, or another queuers?
        if self.group_id == data["group_id"]:
            self.logger.debug(
                f"[magenta]Received task event with status '{data['status']}'"
            )

            if data["status"] in ["SUCCESS", "FAILURE"]:

                # Calculate discrete task progress
                self.logger.debug(f"[magenta]Incrementing discrete task progress")
                self.completed_tasks = self.completed_tasks + 1

                # Decrement worker count on worker finish
                if data["worker"] in self.active_workers:
                    self.active_workers.remove(data["worker"])
                    self.logger.debug(
                        f"[magenta]Removed '{data['worker']}' from worker count, now: "
                        f"{len(self.active_workers)}"
                    )

            # Increment worker count on worker start
            elif data["status"] == "STARTED":
                if data not in self.active_workers:
                    self.active_workers.append(data["worker"])
                    self.logger.debug(
                        f"[magenta]Added '{data['worker']}' to worker count, now: "
                        f"{len(self.active_workers)}"
                    )
            else:
                pass

            # Print task event updates
            worker = data["worker"]
            file_name = data["args"][0]["file_name"]

            switch = {
                "SUCCESS": f"[bold green] :green_circle: {worker}[/] -> finished '{file_name}'",
                "FAILURE": f"[bold red] :red_circle: {worker}[/] -> [red]failed '{file_name}'",
                "STARTED": f"[bold cyan] :blue_circle: {worker}[/] -> picked up '{file_name}'",
            }

            self.status = switch[data["status"]]

    def update_task_info(self):

        self.parse_task_info_data()

        # Update last status in live view
        self.last_status.update(
            task_id=self.last_status_id,
            last_status=self.status,
        )

        # Update task info in live view
        self.progress.update(
            task_id=self.progress_id,
            active_workers=len(self.active_workers),
            completed_tasks=self.completed_tasks,
        )

        # Dealt with data, reset flag
        self.new_task_data_exists = False

    def update_progress_info(self):

        # Get up-to-date average
        try:

            self.total_average_progress = sum(self.prog_percentages.values()) / len(
                self.callable_tasks
            )

        except DivisionByZero:
            self.logger.debug(
                "[yellow]Encountered division by zero error! Setting progress to zero."
            )
            self.total_average_progress = 0.0

        # Update average progress
        self.logger.debug(
            f"[magenta]Total tasks average percentage: {self.total_average_progress}"
        )
        self.progress.update(
            task_id=self.progress_id, completed=self.total_average_progress
        )

        # Dealt with data, reset flag
        self.new_progress_data_exists = False

    def report_progress(self, results):

        self.group_id = results.id

        self.__define_progress_bars()
        self.__init_progress_bars()

        def __pubsub_exception_handler(ex, pubsub, thread):
            print(ex)
            thread.stop()
            thread.join(timeout=1.0)
            pubsub.close()

        # Subscribe to channels
        self.pubsub.psubscribe(**{"celery-task-meta*": self.task_event_handler})
        self.pubsub.psubscribe(**{"task-progress*": self.progress_event_handler})

        with Live(self.progress_group):

            # Run pubsub consumer in separate thread
            sub_thread = self.pubsub.run_in_thread(
                sleep_time=0.001,
                # TODO: Fix run_in_thread exception handler
                # labels: bug
                # exception_handler=__pubsub_exception_handler,
            )

            try:

                while not results.ready():

                    if self.new_task_data_exists:
                        self.update_task_info()

                    if self.new_progress_data_exists:
                        self.update_progress_info()

                    time.sleep(0.001)

            except:

                # re raise
                raise

            finally:

                # Close pubsub connection
                sub_thread.stop()
                sub_thread.join(timeout=1.0)
                self.pubsub.close()

            # Hide the progress bars after finish
            self.last_status.update(task_id=self.last_status_id, visible=False)
            self.progress.update(task_id=self.progress_id, visible=False)

        return results
