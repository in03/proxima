# Proxima :sparkles:
#### (Previously *Resolve Proxy Encoder*)

![GitHub](https://img.shields.io/github/license/in03/proxima) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![GitHub branch checks state](https://img.shields.io/github/checks-status/in03/proxima/main)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/in03/proxima/main.svg)](https://results.pre-commit.ci/latest/github/in03/proxima/main)

![GitHub last commit](https://img.shields.io/github/last-commit/in03/proxima)
![GitHub Repo stars](https://img.shields.io/github/stars/in03/proxima?style=social)


##### Proxima makes queuing proxies from DaVinci Resolve a breeze. Launch the worker on as many computers as you have free and it'll pool all the free CPU threads together to encode multiple proxies at once. Only have the one computer? Encoding runs entirely on the CPU, leaving GPU-heavy Resolve with plenty of resources to continue editing while you pump out proxies. Once they're finished, they're automatically linked.

> **Warning**
>
> **Broker support has changed!**
> Since introducing queuer-side progress indicators, only Redis is supported as a broker. Any other brokers officially supported by Celery will no longer work. 
> Passing progress data back to the queuer through Celery proved to be a little obtuse. Choosing and working with a single broker was the path forward.

![](https://github.com/in03/proxima/blob/main/docs/images/rprox_worker-min.gif)
 
## Why make proxies? ##
DaVinci Resolve's greatly benefits from having all-intra media, like ProRes or DNxHD. If you shoot in h.264 or h.265 like many do, you're likely to see great performance improvements using proxies. This application makes queuing, encoding and linking them quick and easy.

## Features ##
- [x] Distributed encoding on multiple machines
- [x] Utilizes all CPU threads for encoding
- [x] Queue only used proxies straight from a DaVinci Resolve timeline
- [x] Automatically link proxies after encoding
- [x] Flexible queuer/worker arrangement allows background encoding on same machine
- [x] Version constrain prevents incompatabilities between different machines
- [x] Easy YAML based user configuration
- [x] Advanced configuration validation
- [x] Automatically checks for updates
- [x] Control Celery with Celery commands from CLI, even when installed with pipx
- [x] Multi progress-bar [#190](https://github.com/in03/proxima/issues/190)

## Roadmap ##
- [ ] Better Resolve 18 integration
- [ ] Better Apple silicon support
- [ ] Faster config parsing and validation with TOML [#207](https://github.com/in03/proxima/issues/207)
- [ ] Interactive timeline selection [#161](https://github.com/in03/proxima/issues/161)
- [ ] Better resource-utilization with encode-chunking
- [ ] Multiple, customizable proxy-presets with rule-based matching [#201](https://github.com/in03/proxima/issues/201)
- [ ] Easier cross-platform paths via path-mapping
- [ ] Manage configuration from CLI
- [ ] Pre-flight checks - encoding settings validation 
- [ ] UI improvements
- [ ] Monitor Web App

## What about Blackmagic's Proxy Generator? ##
I started this for the company I work for, well before BPG was on the scene. If BPG works better for you, go for it! As it stands BPG won't do any all-intra codecs on Windows, which is a dealbreaker for us. It also works on a watch-folder basis with no filename whitelisting or path-filtering rules. That means EVERY video file becomes a proxy, whether you need it or not. Our workflow often sees the shooter doing a rough assembly of chosen takes as an exported timeline. We simply import this timeline and queue proxies from it. If you work with chronic-overshooters, you'll save a heap of disk space and encoding time queuing proxies from a roughly-organised timeline. 


## Ooh, I want it!

### Prerequisites
- One or more editing computers with DaVinci Resolve Studio installed and scripting enabled
- An always on computer to run the broker (e.g. server, NAS, primary-desktop, Raspberry Pi)
- Worker computers (decent resources, can overlap with editing computers)
- all above machines on LAN and able to access same files via same filepath.

> **Warning**
> 
> **DaVinci Resolve 17 requires Python 3.6.**
> 
> This Python version is end-of-life. No bug-fixes or security-patches are being released anymore. 
> As such, many popular Python packages we depend on are dropping support for Python 3.6. 
> Resolve 18 is now out of public beta. Once Proxima's integration and testing are complete for compatability with 18,
> there will be a final release for Resolve 17 and future development will continue in a later version of Python 3.
> Until then the full, working feature-set is available on the main branch.
> To mitigate dependency conflicts you can try:
>
> - Calling Proxima from a Python 3.6 virtual environment.
> - Install Python 3.6 for Proxima and install a newer Python alongside it for your other needs.
> - Install a tool like *pipx* that isolates Python CLI tools with their own virtual environments but keeps them on path (recommended)

### Installation
Proxima is composed of three major parts:

- the 'queuer' responsible for interfacing with DaVinci Resolve and sending tasks to the broker
- the 'broker' (Redis) that distributes jobs to the workers
- the 'worker' one of potentially many workers responsible for doing the actual encoding

#### CLI
The 'queuer' and 'worker' are bundled together in the CLI app. They are both installed from the same source, called from the same command and share the same configuration file. As such, any computer that has the CLI app installed can both queue proxies (so long as Resolve is set-up) and run workers. Install it with pipx:

``` 
pipx install git+https://github.com/in03/proxima
```

#### Broker
The broker is best installed on an always-on computer or server. If it's not running neither queuers nor workers can communicate.
Very little configuration is required. Just make sure it's accessible over LAN. Since [#190](https://github.com/in03/proxima/pull/190), brokers other than Redis are no longer supported.

Install Redis with docker:
```
docker run -d --name some-redis -p 6379:6379 redis-server --append-only yes
```

#### Monitor
An in-house web-app monitor for Proxima jobs is coming and will include some really helpful, specific features.
Until it's ready, if you want to monitor your jobs, it's a good idea to install Flower - an official monitor for Celery tasks and workers.
Install it with docker alongside your broker:
```
docker run --name flower -e $CELERY_BROKER_URL=redis://192.168.1.171:6379/0 -e FLOWER_PURGE_OFFLINE_WORKERS=300 -d flower
```
Set the IP address and port to the same as your broker container. Don't forget the Redis protocol `redis://`. 
Consider setting `FLOWER_PURGE_OFFLINE_WORKERS` if you don't have a well-defined set of computers to run the workers, or there's potential to change worker hostnames. `300` for example, would clear the list of offline workers every 5 minutes. This just keeps things tidy.


## How do I use it?

```
Usage: proxima [OPTIONS] COMMAND [ARGS]...

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
  celery Inject Celery commands to control tasks and workers
  ```

## Configuration
On first run, you'll be prompted to alter your settings. The app will copy the default settings to the OS user configuration folder. 
- **Linux/Mac:** `$XDG_HOME_CONFIG/proxima/user_settings.yml` (may not open settings automatically)
- **Windows:** `%homepath%/proxima/user_settings.yml`


### Some Key Settings

#### `proxy_path_root`
All proxies will be encoded to this directory. They'll retain the source media's directory structure:
```
paths:
  proxy_path_root: R:/ProxyMedia
``` 

#### `celery`
Celery runs all queuer/worker/broker communications. 
Make sure you set all of the below addresses as per your environment!

```
broker:
  url:  redis://192.168.1.19:6379/0
  job_expires: 3600 # 1 hour (cleared if not received by worker)
  result_expires: 86400 # 1 day (Needed for webapp monitor)
```

> **Warning**
> 
> Make sure you set `result_expires!` to a reasonable value otherwise Redis may run out of memory!
> If you need persistent results, consider configuring Redis for persistence.

#### `worker`
```
worker:
  loglevel: INFO
  terminal_args: [] # use alternate shell? Recommend windows terminal ("wt") on Windows.
  celery_args: [-l, INFO, -P, solo, --without-mingle, --without-gossip]
```
Queuer and worker have separate loglevels to make debugging a little easier if you've got just one worker playing up.

### A Note on Concurrency
Some pretty dangerous concurrency settings were moved out of the configuration settings to prevent accidents. Windows doesn't support pre-forking for concurrency. Actually, Celery doesn't officially support Windows anymore at all. Mac and Linux can pre-fork, but the worker launcher invoked with the `proxima work` command gets around this by launching separate processes with workers named `worker1@host`, `worker2@host`, etc. We're going for the lowest common denominator here. This works fine with Mac and Linux too. It makes monitoring easier and cross-platform behaviour more consistent. For those concerned about the extra overhead who would like to squeeze out every last bit of performance on Mac or Linux, consider injecting the `celery multi` command with `proxima celery`. See [Celery daemonization](https://docs.celeryq.dev/en/master/userguide/daemonizing.html?#init-script-celeryd) 



## How can I contribute?
Hey! Thanks! Any help is appreciated. Please check the [Contribution Guide](https://github.com/in03/proxima/wiki/Contribution-Guide).

