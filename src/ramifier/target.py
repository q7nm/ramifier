import os
from pathlib import Path

from xdg import BaseDirectory

from .log import log_warning
from .utils import ensure_dir


class Target:
    def __init__(
        self,
        name: str,
        path: str,
        backup_path: str,
        max_backups: int,
        interval: dict,
        compression_level: int,
        compression_threads: int,
        ram_path: Path,
    ):
        self.name = name
        self.path = Path(os.path.expandvars(path)).expanduser()
        if backup_path is None:
            self.backup_path = Path(BaseDirectory.xdg_data_home) / "ramifier" / name
        else:
            self.backup_path = Path(os.path.expandvars(backup_path)).expanduser()
        self.interval = interval
        self.max_backups = max_backups
        self.compression_level = compression_level
        self.compression_threads = compression_threads

        self.ram_path = ram_path

        if self.path.is_symlink() and self.path.resolve() == self.ram_path:
            self.path.unlink()
            log_warning(f"Target path will be repaired: {self.path}", self.name)
        elif not self.path.is_dir():
            raise NotADirectoryError(f"{self.path} is not a directory")

        ensure_dir(self.path)
        ensure_dir(self.backup_path)
