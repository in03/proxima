## First Run
Assuming you've followed installation instructions and Proxima is up and running,
you can begin to try it out. Run `proxima` in your terminal. 

```
$ proxima

❌  Checking settings...
No user settings found at path 'C:\Users\in03\.config\proxima\user_settings.yml'
Load defaults now for adjustment? [y/n]:
```
Because no configuration file exists yet, Proxima will ask to create one for you
and open it:

```yaml
---  # Proxima User configuration file

# NOTE: 
# Proxy paths, codecs, resolution, filters, etc are all inherited from the queuer's user configuration.
# 'Celery' and 'Worker' settings are pulled from local user configuration.

app:
  loglevel: INFO
  check_for_updates: true
  update_check_url: "https://github.com/in03/proxima" # If you fork the repo, change this to your fork
  disable_version_constrain: false # DANGEROUS! Allows any version of worker to take jobs. Must be set on queuer and worker. 

paths:
  proxy_path_root: R:/ProxyMedia  # Proxy media retains source folder structure
  ffmpeg_logfile_path: R:/ProxyMedia/@logs

proxy:
  ffmpeg_loglevel: error # "quiet", "panic", "fatal", "error", "warning", "info", "verbose", "debug"
  codec: prores
  vertical_res: "720"
  profile: "0" #422 proxy
  pix_fmt: yuv422p
  audio_codec: pcm_s16le
  audio_samplerate: "48000"
  misc_args: [-hide_banner, -stats]
  ext: .mov

filters:
  # Remove elements from lists to disable filter
  extension_whitelist : [.mov, .mp4, .mxf, .avi] 
  framerate_whitelist : [24, 25, 30, 50, 60]

broker:
  url:  redis://192.168.1.123:6379/0
  job_expires: 3600 # 1 hour (cleared if not received by worker)
  result_expires: 86400 # 1 day (Needed for webapp monitor)

worker:
  loglevel: INFO
  terminal_args: [] # use alternate shell? Recommend windows terminal ("wt") on Windows.
  celery_args: [-l, INFO, -P, solo, --without-mingle, --without-gossip]
```

If this all looks like a little much for you right now, don't stress.
We'll walk through them together.





### Starting Workers
You can start workers on your local machine with `proxima work`.
Proxima will ask you how many workers you'd like to start, 
defaulting to two workers less than the amount of logical cores your CPU has.
For example on a 12 core machine, Proxima will recommend 10 workers.

*Example - Starting one worker*:
```console
$ proxima work 1

✅  Checking settings...

                 _
 ___ ___ ___ _ _|_|_____ ___ 
| . |  _| . |_'_| |     | .'|
|  _|_| |___|_,_|_|_|_|_|__,|
|_|


Git build (cloned 🛠 ) '517cb5d' | Version constraint key 'quizically-queer-quail'
Run proxima --help for a list of commands


Starting workers! 👷 ──────────────────────────────────────────────────────────────────

[13:25:30] INFO     Consuming from queue with key: 'quizically-queer-quail'        

           INFO     NEW WORKER- 3buoc@EMA                                     
```


## The version constraint key
```
$ proxima work 1


                 _
 ___ ___ ___ _ _|_|_____ ___ 
| . |  _| . |_'_| |     | .'|
|  _|_| |___|_,_|_|_|_|_|__,|
|_|


Git build (cloned 🛠 ) '517cb5d' | Version constraint key 'quizically-queer-quail'
Run proxima --help for a list of commands
```
Once started, workers will consume jobs queued with the version constraint key `quizically-queer-quail`.
This key is used to prevent workers from consuming jobs from incompatible queuers.
Using a unique key like this allows cloned git builds, installed git builds and PyPi release builds to work well together so long as the code is the same.
It's also possible to alter this key to force different versions to work together, but not recommended.