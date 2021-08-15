# Structure: <protocol>://<user>:<password>@<IP address>:<port>/<virtual host>
broker_url = 'redis://192.168.1.19:6379/0'

# List of modules to import when the Celery worker starts.
imports = ('proxy_encoder.tasks',)

# Using the database to store task state and results.
result_backend = 'redis://192.168.1.19:6379/0'

# Additional settings
# worker_max_tasks_per_child = 1
# worker_concurrency = 1
acks_late = True
worker_prefetch_multiplier = 1
enable_utc = True,
timezone ='Australia/Brisbane'
result_expires = 18000 # 5 hours
worker_pool_restarts = True