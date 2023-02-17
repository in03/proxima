import logging
import os
from dataclasses import dataclass
from functools import cached_property

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from proxima.app import core
from proxima.app.package import build_info
from proxima.celery import celery_app
from proxima.settings.manager import settings

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")

console = Console()


@dataclass(repr=True)
class _WorkerInfo:
    name: str
    host: str
    vc_key: str
    compatible: bool

    def __repr__(self):
        return str(
            "WorkerInfo("
            f"name: '{self.name}', "
            f"host: '{self.host}', "
            f"vc_key: '{self.vc_key}', "
            f"compatible: {self.compatible}"
            ")"
        )


class WorkerCheck:
    def __init__(self):
        self._workers_info: list[_WorkerInfo] = []
        self.vc_key = os.getenv("PROXIMA_VC_KEY")
        logger.debug(f"[magenta]Idle workers:[/]\n{self.idle_workers}")
        logger.debug(f"[magenta]Busy workers:[/]\n{self.busy_workers}")

    def __len__(self):
        return len(self.get_idle_workers())

    @cached_property
    def total_workers(self):
        return self.idle_workers.extend(self.busy_workers)

    @cached_property
    def idle_workers(self):
        return self.get_idle_workers()

    @cached_property
    def busy_workers(self):
        return self.get_busy_workers()

    @property
    def compatible(self) -> list[_WorkerInfo]:
        return [x for x in self.idle_workers if x.compatible]

    @property
    def incompatible(self) -> list[_WorkerInfo]:
        return [x for x in self.idle_workers if not x.compatible]

    @property
    def compatible_hosts(self) -> set[str]:
        return set([x.host for x in self.incompatible if x.compatible])

    @property
    def incompatible_hosts(self) -> set[str]:
        return set([x.host for x in self.incompatible if not x.compatible])

    @property
    def all_are_compatible(self) -> bool:
        if False in [x.compatible for x in self.idle_workers]:
            return False
        return True

    @property
    def none_are_compatible(self) -> bool:
        if True in [x.compatible for x in self.idle_workers]:
            return False
        return True

    def get_idle_workers(self) -> list[_WorkerInfo]:
        """
        Gets a WorkerInfo object for all idle workers.

        This uses Celery's API to poll active queues.
        Use the `idle_workers` property to avoid re-polling.

        Returns:
            list: List of WorkerInfo objects for all idle workers.
        """

        idle_workers_info = []
        idle_workers = celery_app.control.inspect().active_queues()

        if not idle_workers:
            return idle_workers_info

        for worker, attributes in idle_workers.items():
            worker_vc_key = attributes[0]["routing_key"]

            worker_info = _WorkerInfo(
                name=worker,
                host=str(worker).split("@")[1],
                vc_key=worker_vc_key,
                compatible=worker_vc_key == self.vc_key,
            )
            idle_workers_info.append(worker_info)

        return idle_workers_info

    def get_busy_workers(self) -> list[_WorkerInfo]:
        """
        Gets a WorkerInfo object for all busy workers.

        This uses Celery's API to poll active queues.
        Use the `busy_workers` property to avoid re-polling.

        Returns:
            list: List of WorkerInfo objects for all idle workers.
        """

        # TODO: Get busy workers
        # Seems to be a glitch getting busy workers in this version of Celery.
        # Fix planned for next release Feb or March.
        # This might work, but isn't yet:
        # i = celery_app.control.inspect(timeout=10)
        # i.pattern = self.vc_key + "*"
        # i.limit = 1
        # logger.debug(f"[magenta]Active: {i.active_queues()}")

        busy_workers_info = []
        return busy_workers_info

        if not busy_workers:
            return busy_workers_info

        for worker, attributes in busy_workers.items():
            worker_vc_key = attributes[0]["routing_key"]

            worker_info = _WorkerInfo(
                name=worker,
                host=str(worker).split("@")[1],
                vc_key=worker_vc_key,
                compatible=worker_vc_key == self.vc_key,
            )
            busy_workers_info.append(worker_info)

        return busy_workers_info


class AppStatus:
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.status_text: str = ""
        self.vc_key = os.getenv("PROXIMA_VC_KEY")

        self.build_status()
        self.update_status()
        self.worker_status()

        Rule()

    @cached_property
    def status_panel(self):
        return Panel(
            # title="[bold]Status",
            expand=False,
            title_align="left",
            renderable=self.status_text,
        )

    def update_status(self):
        if not settings.app.check_for_updates:
            self.status_text += "[yellow]Update check disabled\n"
            return

        if build_info.is_pip_updatable is False:
            self.status_text += "[green]Running latest release :runner:\n"
            return

        if build_info.is_pip_updatable is True:
            self.status_text += "[yellow]New release available[/] :sparkles:\n"
            return

    def build_status(self):
        self.status_text += "[bold]\nBuild\n[/]"

        if build_info.is_git_repo:
            if build_info.git_version:
                self.status_text += f"[magenta]Git: {build_info.git_version[:7:]}[/] | "

        self.status_text += (
            f"[green]Release: {build_info.version}[/] | "
            f'[cyan]VC key: "{self.vc_key}"\n'
        )

        if not settings.app.version_constrain:
            self.status_text += "[yellow]Version constrain is disabled! :dragon_face:\n"

    def worker_status(self):
        self.status_text += "[bold]\nWorkers[/]\n"

        w = WorkerCheck()

        idle_worker_count = str(len(w.idle_workers)) if w.idle_workers else "N/A"
        busy_worker_count = str(len(w.busy_workers)) if w.busy_workers else "N/A"

        self.status_text += f"[green]Available {idle_worker_count}[/] | [yellow]Busy {busy_worker_count}"

        if not w.all_are_compatible:
            # Eww... 6 lines of code to add newline every 6 offline hosts...
            incompatible_host_string = [
                el
                for y in [
                    [el, "\n"] if idx % 3 == 2 else el
                    for idx, el in enumerate(w.incompatible_hosts)
                ]
                for el in y
            ]
            incompatible_host_string = ", ".join(w.incompatible_hosts)

            self.status_text += (
                f"[red] | Incompatible {len(w.incompatible)}[/]\n"
                f"[red]These hosts are using a different VC key:\n"
                f"{incompatible_host_string}"
            )

            if not settings.app.version_constrain:
                self.status_text += "\n\n[yellow]WARNING: Jobs will be queued to incompatible workers anyway.\n"
