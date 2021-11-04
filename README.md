# Resolve Proxy Encoder

## Work in progress! ⚠️

 Please excuse anything that doesn't make sense in this repository. I code when I can find the time (which is scarce!) and often I'll leave quick-fixes and band-aid-  solutions sitting pretty. I'm doing my best to separate configuration from code and keep things cross platform, but at times I bend the rules to keep this working   everyday in our specific office environment. If you have the time to contribute to this repo, please do! Forks, PRs, issues and suggestions welcome.

 ---
 
## What's it for? ##
DaVinci Resolve Studio has a fantastic remote-rendering system built-in that allows queuing renders on other networked Resolve computers.
Unfortunately Resolve doesn't have a remote-rendering, or even background-rendering solution for proxies. 
Resolve Proxy Encoder is a Python application that can be used in a similar way to Resolve's remote-rendering system, but for proxies.
 
## How does it work? ##
Resolve Proxy Encoder works using four major parts:
- the Celery app that manages and runs the workers
- the `resolve_queue_proxies` module responsible for interfacing with DaVinci Resolve's python API 
- the broker (Redis or RabbitMQ server) that's responsible for sending data between Celery instances

It's not included here, but there's also a dashboard web-app called 'Flower' that can be used to monitor a Celery system.
There are containers available on DockerHub if you want to monitor tasks constantly.

## What does it need?
This app has a few non-negotiable prerequisites:
- Python 3.6 **ONLY** (DaVinci Resolve's Python API requires it)
- DaVinci Resolve Studio, with scripting set up (read Resolve's scripting README)
- Redis or RabbitMQ broker (preferably running on a NAS or server)
- Worker computers (decent resources, connected to LAN, can access source media and proxies output folder)
- Resolve Proxy Encoder installed on every computer involved except broker

It also makes a few assumptions about the way you have your environment set up:
- Running Windows (Mac OS, Linux and BSD untested - though should be easy to make work)
- All source media is accessible from a signel networked volume / mapped-drive
- All proxies are to be encoded to and accessible from a single networked volume / mapped-drive


## How do I install it?
Install directly with pip:
```
py -3.6 -m pip install git+https://github.com/in03/Resolve-Proxy-Encoder
```

## How can I contribute?
Clone the repo, install dependencies, call from poetry shell:
```
git clone https://github.com/in03/Resolve-Proxy-Encoder
cd Resolve-Proxy-Encoder
py -3.6 -m pip install poetry
py -3.6 -m poetry shell
poetry install
rprox
```
If you're unfamiliar with using Poetry for dependency management and packaging, [give it a look](https://python-poetry.org/docs/basic-usage).

## Usage

```
Usage: rprox [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  link   Manually link proxies from directory to source media in open...
  mon    Launch Flower Celery monitor in default browser new window
  purge  Purge all proxy jobs from all queues
  queue  Queue proxies from the currently open DaVinci Resolve timeline
  work   Prompt to start Celery workers on local machine
  ```
