import json
import redis
import time


class TaskTracker:
    def __init__(self, settings):
        """
        Initialise task tracker

        Args:
            settings (SettingsManager instance)
        """

        self.channel_pattern = "task-progress"
        self.matched_task_ids = []

        broker_url = str(settings["celery"]["broker_url"])
        self._host = str(broker_url.split("redis://")[1].split(":")[0])
        self._port = int(broker_url.split(":")[2].split("/")[0])
        self._db = int(broker_url[-1::])

        self.r = redis.Redis(
            host=self._host, port=self._port, db=self._db, decode_responses=True
        )

    def set_task_progress(
        self, task_id, worker_name, advance, completed, total, output_filename
    ):

        channel = f"{self.channel_pattern}:{task_id}"
        self.r.publish(
            channel,
            json.dumps(
                {
                    "task_id": task_id,
                    "worker_name": worker_name,
                    "advance": advance,
                    "completed": completed,
                    "total": total,
                    "output_filename": output_filename,
                }
            ),
        )

    def subscribe(self):

        p = self.r.pubsub(ignore_subscribe_messages=True)
        p.psubscribe(
            f"{self.channel_pattern}*", "celery-task-meta*"
        )  # See https://github.com/redis/redis-py#publish--subscribe
        self.subscription = p

    def get_data(self, group_id):

        message = self.subscription.get_message()
        if message:

            # Convert json body
            data = json.loads(message["data"])

            # New task found, is it one of ours?
            if message["pattern"] == "celery-task-meta*":
                remote_group_id = data["group_id"]

                if group_id == remote_group_id:
                    self.matched_task_ids.append(data["task_id"])
                    return {"task-event": data}

            # If one of the tasks we queued, print
            if message["pattern"] == "task-progress*":
                if data["task_id"] in self.matched_task_ids:
                    return {"task-progress": data}

        return None
