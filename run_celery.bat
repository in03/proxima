start celery -A proxy_encoder worker --loglevel=info
TIMEOUT /T 10
start celery -A proxy_encoder flower