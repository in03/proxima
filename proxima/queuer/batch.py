from functools import cached_property
import logging
import os
from rich.prompt import Confirm, Prompt
from rich import print
from rich.panel import Panel
from dataclasses import asdict
import json

from proxima.app import core, exceptions
from proxima.queuer import link
from proxima.queuer.job import Job
from proxima.settings import settings

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


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
        try:
            return self.batch[0].project.project_name
        except (KeyError, AttributeError) as e:
            logger.error(f"[red]Can't derive project from batch:\n{e}")
            return None

    @cached_property
    def timeline(self):
        try:
            return self.batch[0].project.timeline_name
        except (KeyError, AttributeError) as e:
            logger.error(f"[red]Can't derive project from batch:\n{e}")
            return None

    @property
    def batch_info(self) -> str:

        els = self.existing_link_success_count
        elf = self.existing_link_failed_count
        elr = self.existing_link_requeued_count

        return str(
            f"[white]"
            f"Project '{self.project}'\n"
            f"Timeline '{self.timeline}'\n"
            f"[/]"
            f"[green]Linked {els} | [yellow]Requeued {elr} | [red]Failed {elf}\n"
            f"[cyan]Queueable now {len(self.batch)}\n"
        )

    @property
    def batch_info_panel(self) -> Panel:
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
                    "settings": x.settings.user_settings,
                }
            )

        return data

    def remove_already_linked(self):
        self.batch = [x for x in self.batch if not x.is_linked]

    def handle_existing_unlinked(self):

        """
        Prompts user to either link or re-render unlinked proxy media that exists in the expected location.
        """

        logger.info(f"[cyan]Checking for existing, unlinked media...")

        existing_unlinked = []
        mismatch_fail = []
        link_success = []

        if self.batch:
            existing_unlinked = [
                x for x in self.batch if not x.is_linked and x.newest_linkable_proxy
            ]

        if len(existing_unlinked) > 0:

            [
                logger.debug(
                    f"[magenta] * Existing unlinked - '{x.source.file_name}' <-> {(core.shorten_long_path(x.newest_linkable_proxy))}"
                )
                for x in existing_unlinked
            ]

            if Confirm.ask(
                f"\n[yellow][bold]{len(existing_unlinked)} source files have existing but unlinked proxy media.\n"
                "[/bold]Would you like to link them? If not they will be re-rendered."
            ):

                from rich.progress import track

                for job in track(
                    existing_unlinked, description="[cyan]Linking...", transient=True
                ):

                    if job.newest_linkable_proxy:
                        try:
                            job.link_proxy(job.newest_linkable_proxy)
                        except exceptions.ResolveLinkMismatchError:
                            mismatch_fail.append(job)
                            logger.error(
                                f"Failed to link {os.path.basename(job.newest_linkable_proxy)}"
                            )
                        else:
                            link_success.append(job)
                            self.batch.remove(job)

                # Prompt to requeue if any failures
                if mismatch_fail:
                    if Confirm.ask(
                        f"[yellow]{len(mismatch_fail)} files failed to link."
                        + "They may be corrupt or incomplete. Re-render them?"
                    ):
                        self.batch.extend(mismatch_fail)

                self.existing_link_success_count = len(link_success)
                self.existing_link_failed_count = len(mismatch_fail)

            else:

                self.existing_link_requeued_count = len(existing_unlinked)
                logger.warning(
                    f"[yellow]Existing proxies will be [bold]OVERWRITTEN![/bold][/yellow]"
                )

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
                    "[green]Looks like all your media is already linked.[/]\n"
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
