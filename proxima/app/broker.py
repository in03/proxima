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

        self.worker_data = dict()
        self.task_data = dict()
        self.last_status = str()
        self.prog_percentages = dict()
        self.active_worker_count = int()
        self.completed_tasks = int()
        self.group_id = None

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
            total_tasks=len(self.callable_tasks),
        )

    def task_event_handler(self, message):

        assert message
        data = dict(**json.loads(message["data"]))

        # Weed out the tasks that we didn't queue
        if data["group_id"] == self.group_id:

            self.logger.debug(f"[magenta]Received task event\n{data}")
            self.worker_data.update({data["worker"]: data["status"]})
            self.task_data.update({data["task_id"]: data})

    def progress_event_handler(self, message):

        assert message
        data = dict(**json.loads(message["data"]))
        self.logger.debug(f"[magenta]Received progress event\n{data}")
        self.prog_percentages.update({data["task_id"]: data["percent"]})

    def update_last_status(self):

        last_key = next(reversed(self.task_data.keys()))
        last_data = self.task_data[last_key]

        switch = {
            "SUCCESS": f"[bold green] :green_circle: {last_data['worker']}[/] -> finished '{last_data['args'][0]['file_name']}'",
            "FAILURE": f"[bold red] :red_circle: {last_data['worker']}[/] -> [red]failed '{last_data['args'][0]['file_name']}'",
            "STARTED": f"[bold cyan] :blue_circle: {last_data['worker']}[/] -> picked up '{last_data['args'][0]['file_name']}'",
        }

        self.last_status = switch[last_data["status"]]

        self.status_view.update(
            task_id=self.status_view_id,
            last_status=self.last_status,
        )

    def update_discrete_completion(self):

        # Create a shallow copy, otherwise...
        # "RuntimeError: dictionary changed size during iteration"
        task_data = self.task_data.copy()
        self.completed_tasks = len(
            [v for v in task_data.values() if v["status"] in ["SUCCESS", "FAILURE"]]
        )
        self.progress.update(
            task_id=self.progress_id,
            completed_tasks=self.completed_tasks,
        )

    def update_worker_count(self):

        # If a worker's last event isn't 'STARTED' consider them inactive
        self.active_worker_count = len(
            [x for x in self.worker_data.values() if x == "STARTED"]
        )
        self.progress.update(
            task_id=self.progress_id,
            active_workers=self.active_worker_count,
        )

    def update_progress_info(self):

        # Get up-to-date average
        try:

            self.total_average_progress = sum(self.prog_percentages.values()) / len(
                self.callable_tasks
            )

        except ZeroDivisionError:
            self.logger.debug(
                "[yellow]Encountered division by zero error! Setting progress to zero."
            )
            self.total_average_progress = 0.0

        # Update average progress
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

                    if self.task_data:
                        self.update_last_status()
                        self.update_discrete_completion()

                    if self.worker_data:
                        self.update_worker_count()

                    if self.prog_percentages:
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
            self.status_view.update(task_id=self.status_view_id, visible=False)
            self.progress.update(task_id=self.progress_id, visible=False)

        return results
