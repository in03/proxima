import re
from commonregex import link
import os
from schema import Schema, And, Optional


settings_schema = Schema(
    {
        "app": {
            "loglevel": lambda s: s
            in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "check_for_updates": bool,
            "update_check_url": lambda s: re.match(link, s),
            "disable_version_constrain": bool,
        },
        "paths": {
            "proxy_path_root": lambda p: os.path.exists(p),
            "ffmpeg_logfile_path": lambda p: os.path.exists(os.path.dirname(p)),
        },
        "proxy": {
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
        "celery": {
            "host_address": str,
            "broker_url": str,
            "flower_url": str,
            "result_backend": str,
            "result_expires": int,
        },
        "worker": {
            "loglevel": lambda s: s
            in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "concurrency": int,
            "prefetch_multiplier": int,
            "max_tasks_per_child": int,
            "terminal_args": list,
            "celery_args": list,
        },
        "chunking": {
            "enable_chunking": bool,
            "chunk_secs": int,
            "increment_regex": str,
            "segment_suffix": str,
            "cleanup_temp_files": bool,
        },
    },
    ignore_extra_keys=True,
)
