import os
import shutil
from pathlib import Path

from .global_settings import GlobalSettings
from .log import log_info, log_warning
from .target import Target
from .utils import ensure_dir, is_tmpfs


def create_symlink(target: Target):
    if target.ram_path.exists():
        shutil.rmtree(target.ram_path)
        log_warning(f"Existing RAM path removed: {target.ram_path}", target.name)

    shutil.move(target.path, target.ram_path)
    os.chmod(target.ram_path, 0o700)
    target.path.symlink_to(target.ram_path, target_is_directory=True)
    log_info(f"Symlink created: {target.path} -> {target.ram_path}", target.name)


def remove_symlink(target: Target):
    if not target.ram_path.exists():
        raise FileNotFoundError(f"{target.ram_path} does not exist, nothing to restore")

    if target.path.is_symlink():
        target.path.unlink()
    elif target.path.exists() and target.path.is_dir():
        shutil.rmtree(target.path)

    shutil.move(target.ram_path, target.path)
    log_info("Restored from RAM", target.name)
