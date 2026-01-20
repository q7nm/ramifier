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

        STATE.update(loaded_state)
    else:
        _save_state()


def mark_start(target: Target):
    STATE["targets"].setdefault(
        target.name,
        {
            "last_backup": None,
            "hash_history": deque(),
            "running": True,
        },
    )
    _save_state()


def mark_running(target: Target):
    STATE["targets"].setdefault(target.name, {})["running"] = True
    _save_state()


def mark_backup(target: Target, backup_file: Path):
    STATE["targets"].setdefault(target.name, {})["last_backup"] = str(backup_file)
    _save_state()


def mark_hash(target: Target, hash: str):
    STATE["targets"].setdefault(target.name, {}).setdefault(
        "hash_history", deque()
    ).append(hash)
    _save_state()


def mark_clean_exit(target: Target):
    STATE["targets"].setdefault(target.name, {})["running"] = False
    log_info("Exited cleanly", target.name)
    _save_state()


def set_hash_history_len(target: Target, hash_history_len: int):
    hash_history = get_hash_history(target)
    STATE["targets"][target.name]["hash_history"] = deque(
        hash_history, hash_history_len
    )
    _save_state()


def get_last_backup(target: Target) -> str:
    return STATE["targets"].get(target.name, {}).get("last_backup")


def get_hash_history(target: Target) -> deque[str]:
    return STATE["targets"].get(target.name, {}).get("hash_history", deque())


def get_running(target: Target) -> bool:
    return STATE["targets"].get(target.name, {}).get("running")


def _save_state():
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
