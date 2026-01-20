from threading import Event, Thread

from .backup import backup_target, restore_target
from .interval import Interval
from .log import log_error, log_info, log_warning
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
    try:
        mark_start(target)

        running = get_running(target)
        last_backup = get_last_backup(target)
        if running and last_backup is not None:
            restore_target(target)
        else:
            _safe_backup_target(target, True)

        create_symlink(target)

        mark_running(target)

        target_interval = Interval(target)
        while not stop_event.is_set():
            interval = target_interval.get_interval()
            stop_event.wait(interval * 60)
            _safe_backup_target(target)

        mark_clean_exit(target)

    except Exception as e:
        log_error(f"Daemon terminated due to error: {e}", target.name)
        return

    finally:
        try:
            remove_symlink(target)
        except FileNotFoundError as e:
            log_warning(e, target.name)


def start_daemon(target: Target, stop_event: Event) -> Thread:
    thread = Thread(target=daemon, args=(target, stop_event))
    thread.start()
    log_info("Daemon started", target.name)
    return thread


def _safe_backup_target(target: Target, force: bool = False):
    try:
        backup_target(target, force)
    except (OSError, PermissionError, FileNotFoundError) as e:
        raise RuntimeError("Filesystem error during backup") from e
    except zstandard.ZstdError as e:
        raise RuntimeError("Compression error during backup") from e
