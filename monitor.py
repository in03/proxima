import os
import socket

import yaml
from celery import Celery

script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "proxy_encoder", "config.yml")) as file: 
    config = yaml.safe_load(file)

# Broker Settings
broker = config['rabbit_mq']
user = broker['user']
pwd = broker['password']
address = broker['address']
vhost = broker['vhost']
protocol = broker['protocol']
backend = broker['backend']



def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    def announce_successful_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print('TASK SUCCEEDED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-failed': announce_failed_tasks,
                'task-successful': announce_successful_tasks,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == '__main__':
    app = Celery(broker=f'{protocol}://{user}:{pwd}@{address}/{vhost}')
    print(f"Stared monitoring on {socket.gethostname()}...")
    my_monitor(app)
