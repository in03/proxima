# Structure: <protocol>://<user>:<password>@<IP address>:<port>/<virtual host>
host_address = '192.168.1.19'
broker_url = f'redis://{host_address}:6379/0'
flower_url = f'http://{host_address}:5555'

# List of modules to import when the Celery worker starts.
imports = (
    'proxy_encoder.tasks',
)

# Using the database to store task state and results.
result_backend = broker_url

# Additional settings
worker_max_tasks_per_child = 1
worker_concurrency = 1

task_serializer = 'pickle'
result_serializer = 'pickle'

accept_content = [
    'json', 
    'pickle',
]

result_accept_content = [
    'json', 
    'pickle',
]

acks_late = True
worker_prefetch_multiplier = 1
enable_utc = True
timezone ='Australia/Brisbane'
result_expires = 18000 # 5 hours
worker_pool_restarts = True