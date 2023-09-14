# Link proxies

import logging
import os

from pydavinci import davinci
from pydavinci.wrappers.mediapoolitem import MediaPoolItem
from rich.console import Console

from proxima import exceptions
from proxima.app import core
from proxima.settings.manager import settings
from proxima.types.job import Job
from proxima.types.media_pool_index import media_pool_index

resolve = davinci.Resolve()
console = Console()

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")
logger.setLevel(settings.app.loglevel)


class ProxyLinker:
    def __init__(self, batch: list[Job]):
        self.jobs = batch
        self.project_name = self.jobs[0].project.project_name

        self.link_success = []
        self.mismatch_fail = []

    def project_is_same(self):
        """
        Check that the project open in Resolve is the same one that was queued.

        """
        try:
            current_project = resolve.project.name

        except exceptions.ResolveNoCurrentProjectError:
            logger.error(
                "Can't get current Resolve project. Looks like Resolve may be closed.\n"
                "Run `proxima queue` when you're ready to link your proxies later.",
                exc_info=True,
            )
            return False

        if current_project != self.project_name:
            logger.error(
                f"Looks like you've changed projects. ('[red]{current_project}[/]' -> '[green]{self.project_name}[/]')\n"
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
        self.jobs = [x for x in self.jobs if not x.is_linked or not x.is_offline]

        if not self.jobs:
            raise exceptions.NoneLinkableError()

    def single_link(
        self, media_pool_item: MediaPoolItem, proxy_media_path: str
    ) -> None:
        """
        Wrapper around Resolve's `LinkProxyMedia` API method.

        Args:
            job (): A Proxima Job

        Raises:
            FileNotFoundError: Occurs when the proxy media file does not exist at `proxy_media_path`.

            exceptions.ResolveLinkMismatchError: Occurs when the method returns False.
            Unfortunately the method returns no error context beyond that.
        """

        if not os.path.exists(proxy_media_path):
            raise FileNotFoundError(
                f"File does not exist at path: '{proxy_media_path}'"
            )

        if not media_pool_item.link_proxy(proxy_media_path):
            raise exceptions.ResolveLinkMismatchError(proxy_file=proxy_media_path)

    def batch_link(self):
        """
        Iterate through media list and link each finished proxy with its media pool item.
        """

        logger.info(f"[cyan]Linking {len(self.jobs)} proxies[/]")

        if not self.project_is_same():
            core.app_exit(1, -1)

        self.remove_unlinkable_jobs()

        # Iterate through all available proxies
        for job in self.jobs:
            logger.debug(
                f"[magenta]Attempting to link job:[/]\n{core.shorten_long_path(job.output_file_path)}"
            )
            logger.info(f"[cyan]:link: '{job.source.file_name}'")

            mpi = media_pool_index.lookup(job.source.media_pool_id)

            try:
                self.single_link(mpi, job.output_file_path)

            except exceptions.ResolveLinkMismatchError:
                show_exception = False
                if logger.getEffectiveLevel() <= 10:
                    show_exception = True

                logger.error(
                    f"[red bold]:x: Failed to link '{job.source.file_name}'[/]\n"
                    f"[red]",
                    exc_info=show_exception,
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
                    "[red]Resolve might not like your encoding settings or something else is wrong.[/]\n",
                    exc_info=True
                    # TODO: Add troubleshooting wiki link here
                    # Like so: `"[cyan]See [troubleshooting](link)"`
                    # labels: enhancement
                )
                core.app_exit(1, -1)
