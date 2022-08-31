#!/usr/bin/env python3.6
# Link proxies

import logging

from rich.console import Console
from typing import Tuple

from proxima import core
from proxima import exceptions
from proxima.settings import SettingsManager
from proxima import resolve

console = Console()
settings = SettingsManager()

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


class ProxyLinker:
    def __init__(self, jobs, linkable_types: list = ["Offline", "None"]):

        self.jobs = jobs
        self.linkable_types = linkable_types

        self.link_success = []
        self.mismatch_fail = []

    def project_is_same(self):
        """
        Check that the project open in Resolve is the same one that was queued.

        """
        try:

            ro = resolve.ResolveObjects()

        except exceptions.ResolveAPIConnectionError:
            logger.error(
                "Can't communicate with Resolve. Maybe it's closed?\n"
                "Run `proxima queue` when you're ready to link your proxies later.",
                exc_info=True,
            )
            return False

        try:

            current_project = ro.project.GetName()

        except exceptions.ResolveNoCurrentProjectError:
            logger.error(
                "Can't get current Resolve project. Looks like Resolve may be closed.\n"
                "Run `proxima queue` when you're ready to link your proxies later.",
                exc_info=True,
            )
            return False

        if current_project != self.jobs[0]["project"]:
            logger.error(
                f"Looks like you've changed projects. ('[red]{current_project}[/]' -> '[green{self.jobs[0]['project']}[/]')\n"
                "Proxies can't be linked to a closed project.\n"
                "Run `proxima queue` when you're ready to link your proxies later."
            )
            return False

        return True

    def remove_unlinkable_jobs(self):
        """
        Remove jobs from the link queue that aren't in `linkable_types`

        This prevents relinking footage that is already linked according to Resolve.
        """
        self.jobs = [x for x in self.jobs if x["proxy_status"] in self.linkable_types]

        if not self.jobs:
            raise exceptions.NoneLinkableError()

    def __link_proxy_media(self, job):
        """
        Wrapper around Resolve's `LinkProxyMedia` API method.

        Args:
            job (): A Proxima Job

        Raises:
            exceptions.ResolveLinkMismatchError: Occurs when the method returns False.
            Unfortunately the method returns no error context beyond that.
        """
        if not job["media_pool_item"].LinkProxyMedia(job["proxy_media_path"]):
            raise exceptions.ResolveLinkMismatchError(
                proxy_file=job["proxy_media_path"]
            )

    def link(self):

        """
        Iterate through media list and link each finished proxy with its media pool item.

        Args:
            jobs (list of dicts): queuable jobs with project, timeline and setting metadata
            linkable_types (list, optional): List of job `proxy_status` values to attempt link on. Defaults to ["Offline", "None"].
            prompt_reiterate(bool, optional): If any links fail, prompt the user to fetch media pool items again by reiterating timelines.
            If prompt_rerender is enabled, prompt_reiterate runs first.
            prompt_rerender (bool, optional): If any links fail, prompt the user to re-queue them. Defaults to False.

        Returns:
            remaining_jobs (list of cits): the remaining queuable jobs that haven't been linked
        """

        logger.info(f"[cyan]Linking {len(self.jobs)} proxies[/]")

        if not self.project_is_same():
            core.app_exit(1, -1)

        self.remove_unlinkable_jobs()

        # Iterate through all available proxies
        for job in self.jobs:

            logger.debug(f"[magenta]Attempting to link job:[/]\n {job}")
            logger.info(f"[cyan]:link: '{job['file_name']}'")

            try:

                self.__link_proxy_media(job)

            except exceptions.ResolveLinkMismatchError:
                logger.error(
                    f"[red bold]:x: Failed to link '{job['file_name']}'[/]\n" f"[red]",
                    # exc_info=True,
                )
                self.mismatch_fail.append(job)

            else:
                logger.info(f"[green bold]:heavy_check_mark: Linked\n")
                self.link_success.append(job)

        if self.link_success:
            logger.debug(f"[magenta]Total link success:[/] {len(self.link_success)}")

        if self.mismatch_fail:
            logger.error(f"[red]{len(self.mismatch_fail)} proxies failed to link!")

            if len(self.mismatch_fail) == len(self.jobs):

                logger.critical(
                    "[red bold]Oh dear. All the proxies failed to link.[/]\n"
                    "[red]Resolve might not like your encoding settings or something else is wrong.[/]\n"
                    # TODO: Add troubleshooting wiki link here
                    # Like so: `"[cyan]See [troubleshooting](link)"`
                    # labels: enhancement
                )
                core.app_exit(1, -1)
