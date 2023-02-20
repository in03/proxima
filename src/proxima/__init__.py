__version__ = "1.0.6"

import logging
import os
import semver

from rich.logging import RichHandler


def setup_rich_logging():
    """Set logger to rich, allowing for console markup."""

    FORMAT = "%(message)s"
    logging.basicConfig(
        level="WARNING",
        format=FORMAT,
        datefmt="[%X]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_extra_lines=1,
                markup=True,
            )
        ],
    )


_semver = semver.VersionInfo.parse(__version__)

os.environ["PROXIMA_VERSION"] = __version__
os.environ["PROXIMA_VC_KEY"] = f"{_semver.major}.{_semver.minor}"

setup_rich_logging()

# TODO: Fix fragile relative imports
# This import order really matters!
# isort is configured not to touch __init__ files
# but this is fragile and should be fixed

from proxima.cli import main as cli

from .app import core
from .celery import shared
from .app import checks
from .app import exceptions
from .app import resolve
from .app.link import ProxyLinker
