import signal
from threading import Event, Thread

from .backup import backup_target, restore_target
from .runtime import create_symlink, get_ram_dir
from .state import STATE, mark_clean_exit, mark_running, mark_start
from .target import Target


def daemon(target: Target, stop_event: Event):
    mark_start(target)

    target_state = STATE["targets"].get(target.name, {})
    running = target_state.get("running")
    if running and target_state.get("last_backup") is not None:
        try:
            restore_target(target, True)
        except FileNotFoundError as e:
            print(e)
            return
    else:
        backup_target(target, True)

    ram_dir = get_ram_dir()
    create_symlink(target, ram_dir)

    mark_running(target)

    while not stop_event.is_set():
        stop_event.wait(target.interval * 60)
        backup_target(target)

    restore_target(target, False)
    backup_target(target)
    mark_clean_exit(target)


def start_daemon(target: Target, stop_event: Event):
    thread = Thread(target=daemon, args=(target, stop_event))
    thread.start()
    return thread
