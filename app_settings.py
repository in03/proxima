""" Application-wide settings.
Submodules have their own adjacent settings files.
"""
# Always need an outer dict
defaults = dict(

    app = dict(
        debug = False,
    ),

    paths = dict(
        proxy_dir = "R:\\ProxyMedia",
        ffmpeg = "C:\\Program Files\\FFMPEG",
        supported_exts = [".mov", ".mp4", ".mxf", ".avi"],
    ),

)
