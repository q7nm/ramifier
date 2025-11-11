import os
import shutil
from pathlib import Path

from .log import log_info, log_warning
from .target import Target
from .utils import ensure_dir, get_ram_dir, is_tmpfs


def create_symlink(target: Target, ram_dir: Path):
    ram_path = ram_dir / target.name
    if ram_path.exists():
        shutil.rmtree(ram_path)
        log_warning(f"Existing RAM path removed: {ram_path}", target.name)
    if target.path.resolve() == ram_dir / target.name:
        target.path.unlink()
        log_warning(f"Target path repaired: {target.path}", target.name)
    shutil.move(target.path, ram_path)
    os.chmod(ram_path, 0o700)
    target.path.symlink_to(ram_path, target_is_directory=True)
    log_info(f"Symlink created: {target.path} -> {ram_path}", target.name)
