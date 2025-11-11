import os
import sys
from pathlib import Path

from xdg import BaseDirectory

from .log import log_error, log_info, log_warning

LOCK_FILE = Path(BaseDirectory.get_runtime_dir()) / "ramifier-0.lock"


def acquire_lock():
    if LOCK_FILE.exists():
        log_warning("Stale lock file found")
        pid = int(LOCK_FILE.read_text())
        try:
            os.kill(pid, 0)
            log_error(f"Daemon already running with PID {pid}")
            sys.exit(1)
        except ProcessLookupError:
            pass
    LOCK_FILE.write_text(str(os.getpid()))
    log_info("Lock acquired")


def release_lock():
    if LOCK_FILE.exists() and int(LOCK_FILE.read_text()) == os.getpid():
        LOCK_FILE.unlink()
