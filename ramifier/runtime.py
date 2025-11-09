import os
import shutil
from pathlib import Path

from .target import Target
from .utils import ensure_dir, is_tmpfs


def get_ram_dir() -> Path:
    shm = Path("/dev/shm")
    tmp = Path("/tmp")
    if is_tmpfs(shm):
        ram_dir = shm / "ramifier"
    else:
        ram_dir = tmp / "ramifier"
    ensure_dir(ram_dir, 0o700)
    return ram_dir


def create_symlink(target: Target, ram_dir: Path):
    ram_path = ram_dir / target.name
    if ram_path.exists():
        shutil.rmtree(ram_path)
    if target.path.resolve() == get_ram_dir() / target.name:
        target.path.unlink()
    shutil.move(target.path, ram_path)
    os.chmod(ram_path, 0o700)
    target.path.symlink_to(ram_path, target_is_directory=True)
