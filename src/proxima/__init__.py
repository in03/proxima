__version__ = "1.0.3"

import os

import semver

_semver = semver.VersionInfo.parse(__version__)

os.environ["PROXIMA_VERSION"] = __version__
os.environ["PROXIMA_VC_KEY"] = f"{_semver.major}.{_semver.minor}"

from proxima.cli import main as cli

from .app import checks, core, exceptions, resolve
from .app.link import ProxyLinker
from .celery import shared
