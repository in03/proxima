# Resolve Proxy Encoder
 Queue proxies for render directly from Resolve using Celery and RabbitMQ.
 This works using four major parts, the Celery worker to run the tasks on other computers,
 the *RESOLVE_queue_proxies.py* script to interface with DaVinci Resolve's API and get the proxies needed for render,
 RabbitMQ (Celery's default broker) to delegate tasks, and Flower to monitor tasks. 
 It's not included here, but there are containers available on DockerHub if you want to constantly monitor tasks.

 The Resolve script makes a few assumptions about your environment and workflow.
 I personally use this workflow within our local office network only. All of our media is stored and managed on a NAS.
 There was previously some complicated overwrite checking logic to protect proxies from being overwritten
 but our NAS frequently has issues with deleting files if they're potentially in use. 
 This script takes the naive approach of simply overwriting proxy files if they exist.
 For this reason, it's recommended you keep your proxy files on a separate volume to your source media.
 If your 'proxy_path_root' is set incorrectly 
---
 ## Prerequisites
 - DaVinci Resolve Studio, with scripting enabled and environment ready
 - RabbitMQ server running and accessible (preferably running on a NAS or server)
 - Computers capable of being workers (encoding video, running python, connected to LAN)

 ## Installing Resolve Script
 Clone the repo, make a virtualenv, activate it and run `pip install -r requirements.txt`.
 You can call python scripts from a Streamdeck if you don't have spaces in the filepath. (Even with quotes it seems to fail)
 Otherwise you can make a shortcut to the script on your desktop or taskbar, or use a program like AutoHotkey to assign the script to a keyboard shortcut.

 ### Installing the worker on Docker
 To run as a container with Docker, pull the image and run it with the relevant environment variables set.
 Check out the .env-sample if you need a reference.

 ### Installing the worker locally 
 To run locally, clone the repo, make a virtualenv, activate it and run `pip install -r requirements.txt`.

 On your workers, run `celery -A proxy_encoder worker`
 For convenience, add a shortcut to **start_worker.bat** to *shell:startup* if you want it to run when Windows starts.
 If you want it to run without logging in, look into starting it as a service.

 Linux is a little hairier depending on cron, systemd and whichever shell you're using.
 Give it a distro-specific Google.