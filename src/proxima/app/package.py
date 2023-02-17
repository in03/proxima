import importlib
import logging
import os
import subprocess
import sys
from distutils.sysconfig import get_python_lib
from functools import cached_property
from pathlib import Path

from git.exc import InvalidGitRepositoryError
from git.repo import Repo

from proxima.settings.manager import settings

logger = logging.getLogger("proxima")
logger.setLevel(settings.app.loglevel)


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


class Build:
    package_name: str
    package_path: str

    def __init__(self, package_name: str, package_path: str):
        self.package_name = package_name
        self.package_path = package_path

        self.git_sha: str | None = None
        self.git_url: str | None = None

        try:
            self.repo = Repo(self.package_path, search_parent_directories=True)
            self.git_sha = self.repo.commit().hexsha
            self.git_url = self.repo.remote("origin").url

        except InvalidGitRepositoryError:
            logger.debug("[magenta]Not a git repository")

    @cached_property
    def version(self) -> str:
        """
        Gets a package's version number.

        This uses a package's `__version__` in the main `__init__.py`
        instead of the more robust `pkg_resources.get_distibution("package").version`
        to allow support for non-installed source code packages.

        Returns:
            str: Package verison number
        """
        this_package = importlib.import_module(self.package_name)
        return this_package.__version__

    @cached_property
    def is_pip_updatable(self) -> bool:
        latest_version = str(
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "{}==random".format(self.package_name),
                ],
                capture_output=True,
                text=True,
            )
        )
        latest_version = latest_version[latest_version.find("(from versions:") + 15 :]
        latest_version = latest_version[: latest_version.find(")")]
        latest_version = latest_version.replace(" ", "").split(",")[-1]

        current_version = str(
            subprocess.run(
                [sys.executable, "-m", "pip", "show", "{}".format(self.package_name)],
                capture_output=True,
                text=True,
            )
        )
        current_version = current_version[current_version.find("Version:") + 8 :]
        current_version = current_version[: current_version.find("\\n")].replace(
            " ", ""
        )

        return True if latest_version == current_version else False

    @property
    def is_git_repo(self) -> bool:
        return bool(self.git_sha)

    @property
    def git_version(self) -> str | None:
        return self.git_sha

    @cached_property
    def is_git_updatable(self) -> bool:
        all_commits = self.repo.iter_commits()
        *_, last_commit = all_commits

        print(all_commits)

        if self.repo.commit == last_commit:
            return False
        return True


package_path = os.path.dirname(str(sys.modules["proxima"].__file__))
build_info = Build("proxima", package_path)
