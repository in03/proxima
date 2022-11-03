from functools import cached_property
import logging

from rich.prompt import Confirm, Prompt
from rich import print
from rich.panel import Panel
from dataclasses import asdict
import json

from proxima.app import core
from proxima.queuer import link
from proxima.queuer.job import Job
from proxima.settings import settings

core.install_rich_tracebacks()
logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


class BatchHandler:
    def __init__(self, batch: list[Job]):

        self.action_taken = False
        self.existing_link_success_count = 0
        self.existing_link_failed_count = 0
        self.existing_link_requeued_count = 0
        self.batch = batch

    @property
    def batch_info(self) -> str:

        project = self.batch[0].project.project_name
        timeline = self.batch[0].project.timeline_name

        els = self.existing_link_success_count
        elf = self.existing_link_failed_count
        elr = self.existing_link_requeued_count

        return str(
            f"[white]"
            f"Project '{project}'\n"
            f"Timeline '{timeline}'\n"
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

    def handle_existing_unlinked(self):

        """
        Prompts user to either link or re-render unlinked proxy media that exists in the expected location.
        """

        logger.info(f"[cyan]Checking for existing, unlinked media.")

        existing_unlinked = [x.newest_linkable_proxy for x in self.batch]
        if len(existing_unlinked) > 0:

            logger.info(f"[yellow]Found {len(existing_unlinked)} unlinked[/]")

            if Confirm.ask(
                f"\n[yellow][bold]{len(existing_unlinked)} source files have existing but unlinked proxy media.\n"
                "[/bold]Would you like to link them? If not they will be re-rendered."
            ):

                self.action_taken = True

                linkable_now = []
                # Reverse to prevent skipping elements
                for x in reversed(self.batch):
                    if x.newest_linkable_proxy in existing_unlinked:
                        linkable_now.append(x)
                        self.batch.remove(x)

                proxy_linker = link.ProxyLinker(linkable_now)
                proxy_linker.link()

                # Prompt to requeue if any failures
                if proxy_linker.mismatch_fail:
                    if Confirm.ask(
                        f"[yellow]{len(proxy_linker.mismatch_fail)} files failed to link."
                        + "They may be corrupt or incomplete. Re-render them?"
                    ):
                        self.batch.extend(proxy_linker.mismatch_fail)

                self.existing_link_success_count = proxy_linker.link_success
                self.existing_link_failed_count = proxy_linker.mismatch_fail

            else:

                self.existing_link_requeued_count = existing_unlinked
                logger.warning(
                    f"[yellow]Existing proxies will be [bold]OVERWRITTEN![/bold][/yellow]"
                )

    def handle_offline_proxies(self):
        """Prompt to rerender proxies that are 'linked' but their media does not exist.

        Resolve refers to proxies that are linked but inaccessible as 'offline'.
        This prompt can warn users to find that media if it's missing, or rerender if intentionally unavailable.
        """

        logger.info(f"[cyan]Checking for offline proxies[/]")
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

                    new_jobs.extend(
                        [
                            x
                            for x in self.batch
                            if x.source.file_name == offline_proxy.source.file_name
                        ]
                    )

                else:
                    print(f"[yellow]Skipping '{offline_proxy.source.file_name}'...")

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
