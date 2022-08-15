import json
import os
import subprocess
from distutils.sysconfig import get_python_lib
from pathlib import Path
from typing import Union

import pkg_resources
import requests


def get_build_info(package_name: str) -> dict:
    """Attempt to find the current commit SHA from the locally installed package or the local GitHub repo.

    Args:
        - package_name (str): The name of the package to get last commit from.

    Returns:
        - dict:
            - build: git/release
            - installed: True/False
            - version: git commit SHA / release version num
    Raises:
        - TypeError: When no versioning can be retrieved
    """

    # Are we running a pip-installed version built from git?
    try:

        dist = pkg_resources.get_distribution(package_name)
        vcs_metadata_file = dist.get_metadata("direct_url.json")
        vcs_metadata = json.loads(vcs_metadata_file)
        package_current_commit = vcs_metadata["vcs_info"]["commit_id"]

    # Assume any failure means not an installed git-repo.
    except KeyError:
        pass
    except TypeError:
        pass
    except FileNotFoundError:
        pass

    else:

        return {
            "build": "git",
            "installed": True,
            "version": package_current_commit.strip(),
        }

    # Are we running a local git-clone version?
    try:

        latest_commit_id = subprocess.check_output(
            'git --no-pager log -1 --format="%H"', stderr=subprocess.STDOUT, shell=True
        ).decode()

        return {
            "build": "git",
            "installed": False,
            "version": latest_commit_id.strip(),
        }

    # Must be running a release install :)
    # Poetry forces a version, so can rely on the version number existing,
    # but will not be accurate if using git
    except subprocess.CalledProcessError as e:
        pass

    release_version = pkg_resources.get_distribution("proxima").version
    return {
        "build": "release",
        "installed": True,
        "version": release_version.strip(),
    }


def get_remote_current_commit(github_url: str) -> Union[str, None]:
    """Attempt to find the the origin GitHub repo's latest commit SHA for the main branch.

    This currently only works with GitHub!

    Args:
        - github_url (str): The URL of the origin repo.

    Returns:
        - remote_current_commit (str): The latest commit's SHA.
        - None: on fail

    Raises:
        - TypeError: Caught by try/except; used to jump between blocks, readability.
    """

    url_list = github_url.split(".com")[1].split("/")
    api_endpoint = (
        f"https://api.github.com/repos/{url_list[1]}/{url_list[2]}/commits/main"
    )

    try:

        r = requests.get(api_endpoint, timeout=8)
        if not str(r.status_code).startswith("2"):
            print(
                f"[red]Couldn't connect to GitHub API\n[/]"
                + f"[yellow]HTTP status code:[/] {r.status_code}\n\n"
            )
            return None

    except Exception as e:
        print(f"[red]Couldn't connect to GitHub API:[/]\n{e}")
        return None

    results = r.json()
    remote_current_commit = results["sha"]
    return remote_current_commit


def get_script_from_package(script_name: str) -> Union[str, None]:
    """Get path to a named script in the current package

    Allows us to call scripts buried in a virtual env like pipx.
    Case insensitive.
    """

    package_dir = Path(get_python_lib()).resolve().parents[1]
    scripts_dir = os.path.join(package_dir, "Scripts")

    for x in os.listdir(scripts_dir):

        file_ = x.lower()
        if script_name.lower() in file_.lower():

            return os.path.abspath(os.path.join(scripts_dir, file_))

    return None
