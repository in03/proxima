__version__ = "1.0.1"

import semver


class VersionConstraint:
    """
    Version constraint key
    used to maintain queuer/worker compatability
    Constrains to package's semver major + minor
    """

    def __init__(self):
        self.version = semver.VersionInfo.parse(__version__)
        self._key = f"{self.version.major}.{self.version.minor}"

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, new_key: str):
        self._key = new_key


version_constraint = VersionConstraint()


from .app import core
from .celery import shared
from .app import checks
from .app import exceptions
from .app import resolve
from .app.link import ProxyLinker

from proxima.cli import main as cli
