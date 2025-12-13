from threading import Event, Thread

from .backup import backup_target, restore_target
from .interval import Interval
from .log import log_info, log_warning
from .runtime import create_symlink, remove_symlink
from .state import (
    get_last_backup,
    get_running,
    mark_clean_exit,
    mark_running,
    mark_start,
)
from .target import Target


def daemon(target: Target, stop_event: Event):
    mark_start(target)

    running = get_running(target)
    last_backup = get_last_backup(target)
    if running and last_backup is not None:
        try:
            restore_target(target)
        except FileNotFoundError:
            log_warning("Backup file not found", target.name)
            return
    else:
        backup_target(target, True)

    create_symlink(target)

    mark_running(target)

    target_interval = Interval(target)
    while not stop_event.is_set():
        interval = target_interval.get_interval()
        stop_event.wait(interval * 60)
        backup_target(target)

    try:
        remove_symlink(target)
    except FileNotFoundError:
        log_warning(
            f"{target.ram_path} does not exist, nothing to restore",
            target.name,
        )

    mark_clean_exit(target)


def start_daemon(target: Target, stop_event: Event) -> Thread:
    thread = Thread(target=daemon, args=(target, stop_event))
    thread.start()
    log_info("Daemon started", target.name)
    return thread
