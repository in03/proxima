start celery -A proxy_encoder worker --loglevel=info --pool=solo
TIMEOUT /T 5
start celery -A proxy_encoder flower
TIMEOUT /T 5
start http://localhost:5555