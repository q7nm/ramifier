import json
import os
from collections import deque
from pathlib import Path
from threading import Lock

from xdg import BaseDirectory

from .log import log_info
from .target import Target
from .utils import ensure_dir

STATE_PATH = Path(BaseDirectory.xdg_state_home) / "ramifier"
STATE_FILE = STATE_PATH / "state.json"
STATE_TEMP_FILE = STATE_FILE.with_suffix(".tmp")
STATE_LOCK = Lock()

STATE = {"targets": {}}


def load_state():
    if STATE_FILE.exists():
        with STATE_FILE.open("r") as f_in:
            loaded_state = json.load(f_in)

        for target in loaded_state.get("targets", {}).values():
            target["mtime_history"] = deque(target.get("mtime_history", []), maxlen=5)
        STATE.update(loaded_state)
    else:
        save_state()


def save_state():
    ensure_dir(STATE_PATH)
    with STATE_LOCK:
        with STATE_TEMP_FILE.open("w") as f_out:
            json.dump(
                STATE,
                f_out,
                default=lambda o: list(o) if isinstance(o, deque) else None,
                indent=4,
            )
        os.replace(STATE_TEMP_FILE, STATE_FILE)


def mark_start(target: Target):
    STATE["targets"].setdefault(
        target.name,
        {
            "path": str(target.path),
            "last_backup": None,
            "mtime_history": deque(maxlen=5),
            "running": True,
        },
    )
    save_state()


def mark_running(target: Target):
    STATE["targets"].setdefault(target.name, {})["running"] = True
    save_state()


def mark_backup(target: Target, backup_file: Path):
    STATE["targets"].setdefault(target.name, {})["last_backup"] = str(backup_file)
    save_state()


def mark_mtime(target: Target, mtime: float):
    STATE["targets"].setdefault(target.name, {}).setdefault(
        "mtime_history", deque(maxlen=5)
    ).append(mtime)
    save_state()


def mark_clean_exit(target: Target):
    STATE["targets"].setdefault(target.name, {})["running"] = False
    log_info("Exited cleanly", target.name)
    save_state()
