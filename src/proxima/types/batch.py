import json
import logging
import os
from dataclasses import asdict
from functools import cached_property

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from proxima.app import core, exceptions
from proxima.settings.manager import settings
from proxima.types.job import Job

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")
logger.setLevel(settings.app.loglevel)

console = Console()


class Batch:
    def __init__(self, batch: list[Job]):
        self.action_taken = False
        self.existing_link_success_count = 0
        self.existing_link_failed_count = 0
        self.existing_link_requeued_count = 0
        self.batch = batch

        # instantiate cached properties
        self.project
        self.timeline

    @cached_property
    def project(self):
        """
        Project name derived from first job in batch.

        Property is cached to prevent KeyError if handler removes all jobs.

        Returns:
            project_name: The name of the Resolve project the job refers to
        """
        try:
            return self.batch[0].project.project_name
        except (KeyError, AttributeError) as e:
            logger.error(f"[red]Can't derive project from batch:\n{e}")
            return None

    @cached_property
    def timeline(self):
        """
        Timeline name derived from first job in batch.

        Timeline is cached to prevent KeyError if handler removes all jobs.

        Returns:
            timeline_name: The name of the Resolve timeline the job refers to
        """
        try:
            return self.batch[0].project.timeline_name
        except (KeyError, AttributeError) as e:
            logger.error(f"[red]Can't derive project from batch:\n{e}")
            return None

    @property
    def batch_info(self) -> str:
        """
        Information about the current batch:
        - project, timeline name
        - Linked, requeued and failed to link existing proxies
        - Proxy preset nickname, write mode: overwrite, unique
        - Total proxies queueable now

        Returns:
            str: A multiline string with batch information
        """

        els = self.existing_link_success_count
        elf = self.existing_link_failed_count
        elr = self.existing_link_requeued_count

        if not settings.proxy.overwrite:
            overwrite_warning = "[yellow]PRESERVE. Use wisely."
        else:
            overwrite_warning = "[magenta]OVERWRITE"

        return str(
            f"[cyan]{self.project} | {self.timeline}[/]\n"
            f"[green]Linked {els} | [yellow]Requeued {elr} | [red]Failed {elf}\n"
            f"{settings.proxy.nickname} | {overwrite_warning}\n"
            f"\n[bold][white]Total queueable now:[/bold] {len(self.batch)}\n"
        )

    @property
    def batch_info_panel(self) -> Panel:
        """
        Batch info displayed in a Rich renderable panel

        Returns:
            Panel: Rich Panel wrapping batch info
        """
        return Panel(
            title="[bold]Batch Info",
            expand=False,
            title_align="left",
            renderable=self.batch_info,
        )

    @cached_property
    def hashable(self) -> list[dict]:
        """
        All hashable class attributes as list of dictionaries

        Used to make job classes JSON serialisable.
        Each class attribute is tested for JSON serialisability(?),
        it's cached for faster subsequent access.

        Returns:
            list[dict]: List of dicts of select class attributes
        """

        def is_jsonable(x):
            try:
                json.dumps(x)
                return True
            except (TypeError, OverflowError):
                return False

        def as_dict(dataclass_):
            return asdict(
                dataclass_,
                dict_factory=lambda x: {k: v for (k, v) in x if is_jsonable(x)},
            )

        data = []
        for x in self.batch:
            job_attributes = {
                "output_file_path": x.output_file_path,
                "output_file_name": x.output_file_name,
                "output_directory": x.output_directory,
                "is_linked": x.is_linked,
                "is_offline": x.is_offline,
                "newest_linkable_proxy": x.newest_linkable_proxy,
                "input_level": x.input_level,
            }

            data.append(
                {
                    "job": job_attributes,
                    "project": as_dict(x.project),
                    "source": as_dict(x.source),
                    "settings": x.settings.dict(),
                }
            )

        return data

    def remove_healthy(self):
        """Remove linked and online source media, i.e. \"healthy\" """
        self.batch = [x for x in self.batch if not x.is_linked or x.is_offline]

    def handle_existing_unlinked(self):
        """
        Prompts user to either link or re-render unlinked proxy media that exists in the expected location.
        """

        logger.info("[cyan]Checking for existing, unlinked media...")

        existing_unlinked = []
        mismatch_fail = []
        link_success = []

        if self.batch:
            existing_unlinked = [
                x for x in self.batch if not x.is_linked and x.newest_linkable_proxy
            ]

        # Set media handled now to 'Online' so the offline handler doesn't catch it
        for x in self.batch:
            if x in existing_unlinked:
                x.is_offline = False

        if len(existing_unlinked) > 0:
            # Log each existing unlinked media and matched proxy source with abbreviated file path
            for x in existing_unlinked:
                logger.debug(
                    f"[magenta] * Existing unlinked - '{x.source.file_name}' <-> {(core.shorten_long_path(x.newest_linkable_proxy))}"
                )

            # Prompt user to relink or rerender
            if not Confirm.ask(
                f"\n[yellow][bold]{len(existing_unlinked)} source files have existing but unlinked proxy media.\n"
                "[/bold]Would you like to link them? If not they will be re-rendered."
            ):
                # Mark all as requeued and carry on
                self.existing_link_requeued_count = len(existing_unlinked)

                if settings.proxy.overwrite:
                    logger.debug("[magenta] * Existing proxies set to be overwritten")
                    # TODO: Implement overwrite logic - also need to test if this is feasible without oplock issues"
                return

            # Handle linking
            from rich.progress import track

            for job in track(
                existing_unlinked, description="[cyan]Linking...", transient=True
            ):
                if not job.newest_linkable_proxy:
                    continue

                try:
                    job.link_proxy(job.newest_linkable_proxy)
                except exceptions.ResolveLinkMismatchError:
                    mismatch_fail.append(job)
                    logger.error(
                        f"[red]Failed to link '{os.path.basename(job.newest_linkable_proxy)}' - proxy does not match source!"
                    )
                else:
                    link_success.append(job)
                    self.batch.remove(job)

            # Mark any successful links
            self.existing_link_success_count = len(link_success)

            # Prompt to requeue any failed links
            if mismatch_fail:
                if not Confirm.ask(
                    f"[yellow]{len(mismatch_fail)} existing proxies failed to link. "
                    + "They may be corrupt or incomplete. Re-render them?"
                ):
                    # Mark failed links as failed and remove
                    [self.batch.remove(x) for x in mismatch_fail]
                    self.existing_link_failed_count = len(mismatch_fail)
                    return

                # Mark failed links as requeued, not offline
                self.existing_link_requeued_count += len(mismatch_fail)

    def handle_offline_proxies(self):
        """Prompt to rerender proxies that are 'linked' but their media does not exist.

        Resolve refers to proxies that are linked but inaccessible as 'offline'.
        This prompt can warn users to find that media if it's missing, or rerender if intentionally unavailable.
        """

        logger.info(f"[cyan]Checking for offline proxies...")

        offline_proxies = []

        if self.batch:
            offline_proxies = [x for x in self.batch if x.is_offline]

        if len(offline_proxies) > 0:
            logger.warning(f"[yellow]Offline proxies: {len(offline_proxies)}[/]")

            choices = ["rerender", "skip", "choose"]
            choice = Prompt.ask(
                f"\n[yellow]{len(offline_proxies)} proxies are offline.[/]\n"
                f"You can choose to rerender them all, skip them all, or choose individually.\n"
                "[cyan]What would you like to do?",
                choices=choices,
                default="rerender",
            )

            assert choice in choices
            print()

            if choice == "rerender":
                self.batch = self.batch
                return

            if choice == "skip":
                return [x for x in self.batch if not x.is_offline]

            new_jobs = []
            for offline_proxy in offline_proxies:
                confirm = Confirm.ask(
                    f"[yellow bold]Offline media:[/] [green]'{offline_proxy.source.file_name}'[/] - "
                    f"[yellow bold]last path: [/][green]'{offline_proxy.source.proxy_media_path}'[/]\n"
                    f"[cyan]Would you like to rerender it?"
                )

                if confirm:
                    print(
                        f"[green]Queuing '{offline_proxy.source.file_name}' for re-render"
                    )

                else:
                    print(f"[yellow]Skipping '{offline_proxy.source.file_name}'...")
                    self.batch.remove(offline_proxy)

                print()

            self.action_taken = True
            self.batch = new_jobs

    def prompt_queue(self):
        """
        Final prompt to confirm number queueable or warn if none.
        """

        logger.debug(
            f"[magenta]Final queueable:[/]\n{[x.source.file_name for x in self.batch]}\n"
        )

        if not self.batch:
            if not self.action_taken:
                print(
                    "[green]No new media to link.[/]\n"
                    "[magenta italic]If you want to re-rerender proxies, unlink them within Resolve and try again."
                )
                return None

            print("[bold][green]All linked up![/bold] Nothing to queue[/] :link:")
            return None

        # Final Prompt confirm
        print()
        if not Confirm.ask("[bold]Send it?[/] :fire:"):
            return False

        return True
