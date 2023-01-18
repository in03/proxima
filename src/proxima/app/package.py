from functools import cached_property
import logging
import json
import os
import subprocess
from distutils.sysconfig import get_python_lib
from pathlib import Path
from shutil import which

from proxima.settings import settings
from pkg_resources import Distribution
import pkg_resources

logger = logging.getLogger("proxima")
logger.setLevel(settings["app"]["loglevel"])

# TODO: Buildinfo might return True to multiple build types
# I think if you're running proxima in a repo and a URL/release is installed...
class BuildInfo:
    def __init__(
        self,
        package_name: str,
        alternate_package_name: str = "",
        git_url: str = "",
        check_timeout: int = 10,
    ):

        self.package_name = package_name
        self.git_url = git_url
        self.alternate_package_name = alternate_package_name
        self.check_timeout = check_timeout

        self.build: str
        self.installed: bool
        self.version: str
        self.dist: Distribution | None

        self._get_distribution()
        self.direct_url_metadata: dict

        if not self.get_build_info():
            raise ValueError(
                f"Package '{package_name}' has no package metadata and is not a git repository.\n"
                "This package may be corrupt, installed in an unsupported way, or simply not installed at all."
            )

    def __repr__(self):
        return str(
            "BuildInfo("
            f"build: '{self.build}', "
            f"installed: {self.installed}, "
            f"version: {self.version}, "
            f"updatable: {self.is_updatable}"
            ")",
        )

    def _get_distribution(self):
        try:
            self.dist = pkg_resources.get_distribution(self.package_name)
            logger.debug(f"[magenta]Got package distribution '{self.package_name}'")
        except pkg_resources.DistributionNotFound as e:
            logger.debug(f"[yellow]Couldn't get package distribution\n{e}")
            self.dist = None

    def get_build_info(self):

        if self.is_git_clone or self.is_url_install or self.is_release_install:
            return True
        return False

    @cached_property
    def is_git_clone(self):
        try:
            latest_commit_id = subprocess.check_output(
                [
                    "git",
                    "--no-pager",
                    "log",
                    "-1",
                    '--format="%H"',
                ],
                stderr=subprocess.STDOUT,
            ).decode()
            logger.debug(f"[magenta]Is git repo: {latest_commit_id}")

        except subprocess.CalledProcessError as e:
            logger.debug(f"[magenta]Git log execution error:\n{e}")
            logger.error(f"Not a git repository!")
            return False

        else:
            self.build = "git"
            self.installed = False
            self.version = latest_commit_id.replace('"', "").strip()
            return True

    @cached_property
    def is_url_install(self):
        if not self.dist:
            return False

        direct_url_file = self.dist.get_metadata("direct_url.json")
        self.direct_url_metadata = json.loads(direct_url_file)
        try:
            vcs_version = (
                self.direct_url_metadata["vcs_info"]["commit_id"]
                .replace('"', "")
                .strip()
            )
        except KeyError:
            logger.debug(
                f"[magenta]No version control metadata found in package's direct_url.json file."
            )
            return False

        self.build = "git"
        self.installed = True
        self.version = vcs_version
        return True

    @cached_property
    def is_release_install(self):
        if not self.dist:
            return False

        if not hasattr(self.dist, "version"):
            return False

        self.release_version = self.dist.version
        self.build = "release"
        self.installed = True
        self.version = self.release_version.replace('"', "").strip()
        if self.version:
            return True

        return False

        if not is_git_clone() and not is_url_install() and not is_release_install():
            return False

    def as_dict(self):
        """
        Return build info as dictionary

        Returns:
            dict: Build info (build, installed, version)
        """
        return {
            "build": self.build,
            "installed": self.installed,
            "version": self.version,
            "updatable": self.is_updatable,
        }

    @cached_property
    def is_updatable(self) -> bool | None:
        """
        Whether or not the package has since been updated

        URL installs and local cloned builds will check against the GitHub repo.
        Currently only GitHub is supported, as it uses GitHub's API.

        Release builds installed via pip or pipx will be checked against PyPi.
        If `alternate_package_name` is defined, it will be used instead of the package
        name defined on init. This is useful when the official package name doesn't match
        the name on PyPi: e.g. `proxima` and `resolve-proxima`

        Returns:
            - `True` if updatable
            - `False` if not updatable
            - `None` if update check failed
        """

        def _git_commit_compare():

            if not self.git_url:
                logger.debug(
                    "[magenta]User provided no git url. Attempting release check only."
                )
                return

            try:
                output = subprocess.check_output(
                    [
                        "git",
                        "ls-remote",
                        self.git_url,
                    ]
                )
            except subprocess.CalledProcessError as e:

                logger.error(f"[red]Couldn't check git repository:\n{e}")
                return None

            head = output.splitlines()[0].decode()
            latest_commit = head.split("\t")[0]

            if self.version != latest_commit:
                return True
            return False

        def _pip_release_version_compare():

            if not which("pip"):
                logger.error(
                    f"[red]Update-check failed to check release build.\n"
                    "Couldn't find 'pip' on path."
                )
                return None

            try:
                output = subprocess.check_output(
                    [
                        "pip",
                        "list",
                        "--outdated",
                    ],
                    timeout=self.check_timeout,
                )
            except subprocess.CalledProcessError as e:

                logger.error(
                    f"[red]Update-check failed to check release build.\n"
                    f"Couldn't run pip. Please check manually:\n{e}"
                )
                return None

            except subprocess.TimeoutExpired as e:
                logger.error(
                    f"[red]Update-check failed to check release build."
                    "'Outdated' check timed out. Please check manually."
                )
                return None

            lines = [x.decode() for x in output.splitlines()]

            if self.alternate_package_name:
                if self.alternate_package_name in lines:
                    return True

            elif self.package_name in lines:
                return True

            return False

        def _pipx_release_version_compare():
            if not which("pipx"):
                logger.error(
                    f"[red]Update-check failed to check release build.\n"
                    "Couldn't find 'pipx' on path."
                )
                return None

            try:
                output = subprocess.check_output(
                    [
                        "pipx",
                        "list",
                        "--outdated",
                    ],
                    timeout=self.check_timeout,
                )
            except subprocess.CalledProcessError as e:

                logger.error(
                    f"[red]Update-check failed to check release build.\n"
                    f"Couldn't run pip. Please check manually:\n{e}"
                )
                return None

            except subprocess.TimeoutExpired as e:
                logger.error(
                    f"[red]Update-check failed to check release build."
                    "'Outdated' check timed out. Please check manually."
                )
                return None

            lines = [x.decode() for x in output.splitlines()]
            if self.package_name in lines:
                return True

        assert self.build
        assert self.version

        if self.build == "git":
            return _git_commit_compare()

        if self.build == "release":

            updatable = _pip_release_version_compare()
            if updatable == False:
                return updatable

            if updatable == None:
                return _pipx_release_version_compare()


def get_script_from_package(script_name: str) -> str:
    """
    Get path to a named script in the current package

    Allows us to call scripts buried in a virtual env like pipx.
    Case insensitive.

    Args:
        script_name (str): The name of the script to locate, e.g. "Celery"

    Raises:
        ImportError: Raised when the script can't be found

    Returns:
        script_path (str): Absolute path to the installed script
    """

    package_dir = Path(get_python_lib()).resolve().parents[1]
    scripts_dir = os.path.join(package_dir, "Scripts")

    for x in os.listdir(scripts_dir):

        file_ = x.lower()
        if script_name.lower() in file_.lower():

            return os.path.abspath(os.path.join(scripts_dir, file_))

    raise ImportError(
        f"Couldn't find {script_name} script in Proxima package."
        "Proxima may need reinstallation!"
    )


build_info = BuildInfo(
    package_name="proxima",
    git_url=settings["app"]["update_check_url"],
)
