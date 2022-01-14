import os
from schema import Schema, And, Optional, Use


config_schema = Schema(
    [
        {
            "loglevel": lambda s: s
            in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "paths": {
                "proxy_path_root": lambda p: os.path.exists(p),
            },
            "proxy_settings": {
                "vid_codec": str,
                "h_res": Use(int),
                "v_res": Use(int),
                "vid_profile": str,
                "pix_fmt": str,
                "audio_codec": str,
                "audio_samplerate": Use(int),
                Optional("misc_args"): list,
                "ext:": And(str, lambda s: s.startswith(".")),
            },
            "filters": {
                "use_extension_whitelist": bool,
                "extension_whitelist": And(
                    list, lambda l: all(map(lambda s: s.startswith("."), l))
                ),
                "use_framerate_whitelist": bool,
                "framerate_whitelist": And(
                    list, lambda l: all(map(lambda s: s.isdigit(), l))
                ),
            },
            "celery_settings": {
                "host_address": str,
                "broker_address": str,
                "flower_address": str,
                "result_backend": str,
                "result_expires": int,
                "worker_loglevel": lambda s: s
                in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                "worker_concurrency": int,
                "worker_prefetch_multiplier": int,
                "worker_max_tasks_per_child": int,
                "worker_use_win_terminal": bool,
                "worker_start_mimized": bool,
            },
        }
    ]
)
