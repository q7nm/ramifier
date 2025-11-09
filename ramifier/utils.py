from datetime import datetime
from pathlib import Path

from psutil import disk_partitions


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M")


def is_tmpfs(path: Path) -> bool:
    path = str(path.resolve())
    partitions = sorted(
        disk_partitions(all=True), key=lambda p: len(p.mountpoint), reverse=True
    )
    for part in partitions:
        if path.startswith(part.mountpoint):
            return part.fstype == "tmpfs"
    return False


def ensure_dir(path: Path, mode: int = None):
    if mode is not None:
        path.mkdir(parents=True, exist_ok=True, mode=mode)
    else:
        path.mkdir(parents=True, exist_ok=True)
