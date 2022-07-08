import json
import redis


class TaskTracker:
    def __init__(self, settings):
        """
        Initialise task tracker

        Args:
            settings (SettingsManager instance)
        """

        broker_url = str(settings["celery"]["broker_url"])
        self._host = str(broker_url.split("redis://")[1].split(":")[0])
        self._port = int(broker_url.split(":")[1].split("/")[0])
        self._db = int(broker_url[-1::])

        self.r = redis.Redis(host=self._host, port=self._port, db=self._db)

    def set_task_progress(self, task_id, frac_n, frac_d):

        channel = f"task:{task_id}:progress"
        self.r.publish(
            channel, json.dumps({"numerator": frac_n, "denominator": frac_d})
        )
