broker_url = 'amqp://marco:yolo@192.168.1.19:5672/marco_vhost'

# List of modules to import when the Celery worker starts.
imports = ('proxy_encoder.tasks',)

## Using the database to store task state and results.
result_backend = 'rpc://'

# Additional settings
worker_prefetch_multiplier = 1
enable_utc = True,
timezone ='Australia/Brisbane'