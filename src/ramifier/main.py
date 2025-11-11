import signal
from threading import Event

from .config import load_config
from .daemon import start_daemon
from .lock import acquire_lock, release_lock
from .state import load_state


def main():
    acquire_lock()
    targets = load_config()
    load_state()

    stop_event = Event()

    def handle_termination(sig, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, handle_termination)
    signal.signal(signal.SIGTERM, handle_termination)

    threads = [start_daemon(target, stop_event) for target in targets]

    for thread in threads:
        thread.join()

    release_lock()
