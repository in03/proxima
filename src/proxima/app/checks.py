from dataclasses import dataclass
from functools import cached_property
import logging

from proxima.app import core
from proxima.celery import celery_app
from proxima.celery import get_queue
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel
from pyfiglet import Figlet
from proxima.app.package import build_info
from proxima.settings import settings

core.install_rich_tracebacks()
logger = logging.getLogger("proxima")

console = Console()


@dataclass(repr=True)
class _WorkerInfo:
    name: str
    host: str
    version_constraint_key: str
    compatible: bool

    def __repr__(self):
        return str(
            "WorkerInfo("
            f"name: '{self.name}', "
            f"host: '{self.host}', "
            f"vc_key: '{self.version_constraint_key}', "
            f"compatible: {self.compatible}"
            ")"
        )


class WorkerCheck:
    def __init__(self):

        self._workers_info: list[_WorkerInfo] = []

        try:
            self.vc_key: str = get_queue()
        except ValueError and FileNotFoundError as e:
            raise ValueError(f"Couldn't read version constraint key: {e}")

        logger.debug(f"[magenta]Idle workers:[/]\n{self.idle_workers}")

    def __len__(self):
        return len(self.get_idle_workers())

    @cached_property
    def idle_workers(self):
        return self.get_idle_workers()

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
                version_constraint_key=worker_vc_key,
                compatible=worker_vc_key == self.vc_key,
            )
            idle_workers_info.append(worker_info)

        return idle_workers_info


class AppStatus:
    def __init__(self, package_name: str):

        self.package_name = package_name
        self.status_text: str = ""
        self.vc_key: str = get_queue()

        self.build_status()
        self.update_status()
        self.worker_status()

        Rule()

    @property
    def banner(self):
        fig = Figlet(font="rectangles")
        return fig.renderText(self.package_name)

    @cached_property
    def status_panel(self):

        return Panel(
            # title="[bold]Status",
            expand=False,
            title_align="left",
            renderable=self.status_text,
        )

    def update_status(self):

        if not settings["app"]["check_for_updates"]:
            self.status_text += "[yellow]Update check disabled\n"
            return

        if build_info.is_updatable == None:
            self.status_text += "[red]Couldn't get latest update :x:\n"
            return

        if build_info.is_updatable == True:
            self.status_text += f"[green]Update available[/] :sparkles:\n"
            return

        if build_info.is_updatable == False:
            self.status_text += "[cyan]Running latest :runner:\n"
            return

    def build_status(self):

        self.status_text += "[bold]\nBuild\n[/]"

        if build_info.is_release_install:

            self.status_text += (
                f"{str(build_info.build).capitalize()} "
                f"Version: {build_info.version} | "
                f"VC key: '{self.vc_key}'\n"
            )

        else:

            self.status_text += (
                f"{str(build_info.build).capitalize()} "
                f"{'([green]installed[/] :package:)' if build_info.installed else '([yellow]cloned[/] :hammer_and_wrench:)'} | "
                f"'{build_info.version[:7:]}' | "
                f"VC key: '{self.vc_key}'\n"
            )

            if settings["app"]["disable_version_constrain"]:
                self.status_text += (
                    "[yellow]Version constrain is disabled! :dragon_face:"
                )

    def worker_status(self):

        self.status_text += "[bold]\nWorkers[/]\n"

        w = WorkerCheck()

        self.status_text += (
            f"[green]Available {len(w.idle_workers)}[/] | " "[yellow]Busy N/A"
        )

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
                f"[red]Proxima on these hosts may be out-of-date:\n"
                f"{incompatible_host_string}"
            )

            if settings["app"]["disable_version_constrain"]:

                self.status_text += f"[yellow]WARNING: Jobs will be queued to incompatible workers anyway."
