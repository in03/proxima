broker_url = 'amqp://guest:guest@localhost:5672/'

# List of modules to import when the Celery worker starts.
imports = ('proxy_encoder.tasks',)

## Using the database to store task state and results.
result_backend = 'rpc://'

# ADDITIONAL SETTINGS
# For our long running tasks, prefetching several tasks causes more problems than it solves.
worker_prefetch_multiplier = 1 
enable_utc = True,
timezone ='Australia/Brisbane' #Brisneyland
result_expires = 18000 # 5 hours

# Allow Flower to restart workers
worker_pool_restarts = True
