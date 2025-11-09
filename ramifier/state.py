import json
import threading
from pathlib import Path

from xdg import BaseDirectory

from .target import Target
from .utils import ensure_dir

STATE_PATH = Path(BaseDirectory.xdg_state_home) / "ramifier"
STATE_FILE = STATE_PATH / "state.json"
STATE_LOCK = threading.Lock()

STATE = {"targets": {}}


def load_state():
    if STATE_FILE.exists():
        with STATE_FILE.open("r") as f_in:
            STATE.update(json.load(f_in))
    else:
        save_state()


def save_state():
    ensure_dir(STATE_PATH)
    with STATE_LOCK:
        with STATE_FILE.open("w") as f_out:
            json.dump(STATE, f_out, indent=4)


def mark_start(target: Target):
    STATE["targets"].setdefault(
        target.name,
        {
            "path": str(target.path),
            "last_backup": None,
            "mtime": None,
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
    STATE["targets"].setdefault(target.name, {})["mtime"] = mtime
    save_state()


def mark_clean_exit(target: Target):
    STATE["targets"].setdefault(target.name, {})["running"] = False
    save_state()
