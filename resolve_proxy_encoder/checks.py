import time
from typing import Union

from rich import print
from rich.console import Console
from rich.prompt import Confirm

from resolve_proxy_encoder.helpers import (
    app_exit,
    get_package_current_commit,
    get_remote_latest_commit,
    get_rich_logger,
    install_rich_tracebacks,
)
from resolve_proxy_encoder.settings.app_settings import Settings
from resolve_proxy_encoder.worker.celery import app as celery_app

install_rich_tracebacks()
logger = get_rich_logger("WARNING")

settings = Settings()
config = settings.user_settings


def check_for_updates(github_url: str, package_name: str) -> Union[str, None]:
    """Compare git origin to local git or package dist for updates

    Args:
        - github_url(str): origin repo url
        - package_name(str): offical package name

    Returns:
        - none

    Raises:
        - none
    """

    console = Console()

    with console.status("[cyan]Checking for updates...[/]\n"):
        remote_latest_commit = get_remote_latest_commit(github_url)

    package_latest_commit = get_package_current_commit(package_name)

    if not remote_latest_commit or not package_latest_commit:
        logger.warning("[red]Failed to check for updates[/]")
        return

    if remote_latest_commit != package_latest_commit:

        logger.warning(
            "[yellow]Update available.\n"
            + "Fully uninstall and reinstall when possible:[/]\n"
            + '"pip uninstall resolve-proxy-encoder"\n'
            + f'"pip install git+{github_url}"\n'
        )

        logger.info(f"Remote: {remote_latest_commit}")
        logger.info(f"Current: {package_latest_commit}")

    else:
        # TODO: Fix too much newline padding when all checks pass
        # Move the newline padding from these 'success prints' to
        # the warning and error logs. Make sure newline padding is consistent.
        # labels: bug
        print("\n[green]Installation up-to-date :white_check_mark:[/]\n")

    return


def check_worker_compatability():

    if config["celery_settings"]["disable_worker_compatability_check"]:
        logger.warning(
            "[yellow]Worker compatability check disabled in user settings![/]\n"
        )
        time.sleep(2)
        return

    # TODO: Stop console status spinner from breaking prompts and console logging
    # Maybe the spinner doesn't expect console output until we've exited the 'with'?
    # labels: bug
    console = Console()
    with console.status(
        "\n[cyan]Fetching online workers for compatability check...[/]\n"
    ):

        # Get online workers and package current commit
        online_workers = celery_app.control.inspect().active_queues()
        git_full_sha = get_package_current_commit("resolve_proxy_encoder")

    if git_full_sha is None:
        logger.warning(
            "[yellow]Couldn't get local package git commit SHA\n"
            + "Any incompatible workers will not be reported.\n"
            + "[red]CONTINUE AT OWN RISK![/]"
        )
        return

    git_short_sha = git_full_sha[::8]

    if online_workers is None:
        logger.warning(
            "[yellow]No workers found. Can't check compatability.\n"
            + "Jobs may not be received if no compatible workers are available!\n[/]"
            + "[red]CONTINUE AT OWN RISK![/]\n\n"
        )
        return None

    logger.debug(f"Online workers: {online_workers}")

    # Get incompatible workers
    incompatible_workers = []
    for worker, attributes in online_workers.items():

        routing_key = attributes[0]["routing_key"]

        # Strip whitespace
        routing_key = "".join(routing_key.split())
        git_short_sha = "".join(git_short_sha.split())

        # Compare git sha
        if not routing_key == git_short_sha:

            incompatible_workers.append(
                {
                    "name": worker,
                    "host": str(worker).split("@")[1],
                    "routing_key": routing_key,
                }
            )

    incompatible_hosts = set()
    for x in incompatible_workers:
        incompatible_hosts.add(x["host"])

    # Prompt incompatible workers
    if incompatible_workers:
        logger.warning(
            f"[yellow]Incompatible workers detected!\n"
            + f"{len(incompatible_workers)}/{len(online_workers)} workers across "
            + f"{len(incompatible_hosts)} host(s) will NOT be able to process jobs queued here.\n"
            + f"[green]To fix, update Resolve Proxy Encoder on below hosts to match git commit SHA, [/]'{git_short_sha}':\n"
            + "', '".join(incompatible_hosts)
            + "\n"
        )

        # If no compatible workers are available
        if len(online_workers) == len(incompatible_workers):

            logger.error(
                "[red]All online workers are incompatible!\n" + "Cannot continue[/]"
            )
            app_exit(1, -1)

        else:

            if Confirm.ask("[cyan]Do you wish to continue?[/]"):
                print("\n")
                return

            print("[yellow]Exiting...[/]")
            app_exit(1, -1)

    print("\n[green]All workers compatible :white_check_mark:[/]\n")
    return
