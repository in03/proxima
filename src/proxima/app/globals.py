import logging
from proxima.settings import settings
from proxima import __version__
import semver

# Logging
logger = logging.getLogger("proxima")
logger.setLevel(settings["app"]["loglevel"])

# Version
package_version = __version__
logger.debug(f"[magenta]Version: {package_version}")
__ver = semver.VersionInfo.parse(package_version)

# Version constraint key
# used to maintain queuer/worker compatability
# Constrains to package's semver major + minor
version_constraint_key = f"{__ver.major}.{__ver.minor}"
logger.debug(f"[magenta]VC key: {version_constraint_key}")
