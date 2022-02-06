import re
from commonregex import link
import os
from schema import Schema, And, Optional


settings_schema = Schema(
    {
        "loglevel": lambda s: s in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "updates": {
            "github_url": lambda s: re.match(link, s),
            "warn_updates": bool,
        },
        "paths": {
            "proxy_path_root": lambda p: os.path.exists(p),
        },
        "proxy_settings": {
            "ffmpeg_loglevel": lambda l: l
            in [
                "quiet",
                "panic",
                "fatal",
                "error",
                "warning",
                "info",
                "verbose",
                "debug",
            ],
            "vid_codec": str,
            "h_res": str,
            "v_res": str,
            "vid_profile": str,
            "pix_fmt": str,
            "audio_codec": str,
            "audio_samplerate": str,
            Optional("misc_args"): list,
            "ext": And(str, lambda s: s.startswith(".")),
        },
        "filters": {
            "use_extension_whitelist": bool,
            "extension_whitelist": And(
                list, lambda l: all(map(lambda s: s.startswith("."), l))
            ),
            "use_framerate_whitelist": bool,
            "framerate_whitelist": And(list, lambda l: all(map(lambda s: int(s), l))),
        },
        "celery_settings": {
            "host_address": str,
            "broker_url": str,
            "flower_url": str,
            "result_backend": str,
            "result_expires": int,
            "worker_loglevel": lambda s: s
            in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "disable_worker_compatability_check": bool,
            "worker_concurrency": int,
            "worker_prefetch_multiplier": int,
            "worker_max_tasks_per_child": int,
            "worker_terminal_args": list,
            "worker_celery_args": list,
        },
    },
    ignore_extra_keys=True,
)
