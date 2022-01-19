import os
from schema import Schema, And, Optional, Use


settings_schema = Schema(
    {
        "loglevel": lambda s: s in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
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
            "h_res": Use(str),
            "v_res": Use(str),
            "vid_profile": str,
            "pix_fmt": str,
            "audio_codec": str,
            "audio_samplerate": Use(str),
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
            "worker_concurrency": int,
            "worker_prefetch_multiplier": int,
            "worker_max_tasks_per_child": int,
            "worker_use_win_terminal": bool,
            "worker_start_minimized": bool,
        },
    }
)
