import logging
from celery import group
from proxima import ProxyLinker, shared, core
from proxima.app import resolve
from proxima.settings import settings
from proxima.celery.tasks import encode_proxy
from rich import print
from pydavinci import davinci
from proxima.app import resolve
from proxima import cli
from rich.panel import Panel
from pydavinci.exceptions import TimelineNotFound


core.install_rich_tracebacks()

logger = logging.getLogger(__name__)
logger.setLevel(settings["app"]["loglevel"])


def queue_batch(batch: list):
    """Block until all queued tasks finish, notify results."""

    logger.info("[cyan]Queuing batch...")

    # Wrap task objects in Celery task function
    callable_tasks = [encode_proxy.s(x) for x in batch]

    # Create task group to retrieve job results as batch
    task_group = group(callable_tasks)

    progress = shared.ProgressTracker()

    # Queue job
    results = task_group.apply_async(expires=settings["broker"]["job_expires"])
    logger.debug(f"[magenta] * Queued batch with ID {results}[/]")

    # report progress is blocking!
    final_results = progress.report_progress(results)
    return final_results


def main():
    """Main function"""

    r_ = davinci.Resolve()

    try:

        track_items = resolve.get_timeline_items(r_.active_timeline)

    except TimelineNotFound:
        core.app_exit(1, -1)

    media_pool_items = resolve.get_media_pool_items(track_items)
    batch = resolve.generate_batch(media_pool_items, settings)

    batch.remove_already_linked()
    batch.handle_existing_unlinked()
    batch.remove_already_linked()
    batch.handle_offline_proxies()

    print(
        Panel(
            expand=False,
            title_align="left",
            renderable=(
                cli.app_status.status_text
                + "\n\n[bold white]Jobs[/][/]\n"
                + batch.batch_info
            ),
        )
    )

    # Prompt the user to queue
    # Confirm exit if nothing to queue, exit directly if user cancels

    cont = batch.prompt_queue()
    if cont == None:
        core.app_exit(0, -1)
    if cont == False:
        raise KeyboardInterrupt

    core.notify(f"Started encoding job '{r_.project.name} - {r_.active_timeline.name}'")

    # Queue tasks to workers and track task progress
    results = queue_batch(batch.hashable)

    if results.failed():
        fail_message = "Some videos failed to encode!"
        print(f"[red]{fail_message}[/]")
        core.notify(fail_message)

    # Notify complete
    complete_message = f"Completed encoding {results.completed_count()} proxies."
    print(f"[green]{complete_message}[/]")
    print("\n")

    core.notify(complete_message)

    _ = results.join()  # Must always call join, or results don't expire

    proxy_linker = ProxyLinker(batch.batch)

    try:
        proxy_linker.batch_link()

    except Exception:

        logger.error(
            f"[red]Couldn't link jobs. Unhandled exception:[/]\n", exc_info=True
        )
        core.app_exit(1, -1)

    else:
        print("[bold][green]All linked up![/bold] Nothing to queue[/] :link:")
        core.app_exit(0)


# TODO: Refactor queue module
# This module should be CLI/API agnostic
# Move interactivity to the CLI module, then this queue module can move to 'app'

if __name__ == "__main__":
    main()
