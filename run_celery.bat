start py -3.9 -m celery -A proxy_encoder worker --loglevel=info
TIMEOUT /T 10
start py -3.9 -m celery -A proxy_encoder flower