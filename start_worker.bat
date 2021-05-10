start %~dp0/proxy_env/Scripts/python.exe -m celery -A proxy_encoder worker --loglevel=info
start http://192.168.1.19:5555