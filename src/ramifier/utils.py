import hashlib
from datetime import datetime
from pathlib import Path

from psutil import disk_partitions


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def is_tmpfs(path: Path) -> bool:
    path = str(path.resolve())
    partitions = sorted(
        disk_partitions(all=True), key=lambda p: len(p.mountpoint), reverse=True
    )
    for part in partitions:
        if path.startswith(part.mountpoint):
            return part.fstype == "tmpfs"
    return False


def get_ram_dir() -> Path:
    shm = Path("/dev/shm")
    tmp = Path("/tmp")
    if is_tmpfs(shm):
        ram_dir = shm / "ramifier"
    else:
        ram_dir = tmp / "ramifier"

    ensure_dir(ram_dir, 0o700)
    return ram_dir


def get_file_hash(path: Path) -> str:
    sha256_hasher = hashlib.sha256()
    with path.open("rb") as f_in:
        for chunk in iter(lambda: f_in.read(8192), b""):
            sha256_hasher.update(chunk)

    return sha256_hasher.hexdigest()


def get_tree_state_hash(path: Path) -> str:
    sha256_hasher = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if not item.is_file():
            continue

        try:
            stat = item.stat()
        except (FileNotFoundError, PermissionError):
            continue

        sha256_hasher.update(str(item.relative_to(path)).encode())
        sha256_hasher.update(str(int(stat.st_mtime)).encode())

    return sha256_hasher.hexdigest()


def ensure_dir(path: Path, mode: int = None):
    if mode is not None:
        path.mkdir(parents=True, exist_ok=True, mode=mode)
    else:
        path.mkdir(parents=True, exist_ok=True)
