import os
from pathlib import Path

from xdg import BaseDirectory

from .utils import ensure_dir, get_ram_dir


class Target:
    def __init__(
        self,
        name: str,
        path: str,
        backup_path: str,
        max_backups: int,
        interval: int,
        dynamic_interval: bool,
        max_dynamic_interval: int,
    ):
        self.name = name
        self.path = Path(os.path.expandvars(path)).expanduser()
        if backup_path is None:
            self.backup_path = Path(BaseDirectory.xdg_data_home) / "ramifier" / name
        else:
            self.backup_path = Path(os.path.expandvars(backup_path)).expanduser()
        self.max_backups = max_backups
        self.interval = interval
        self.dynamic_interval = dynamic_interval
        self.max_dynamic_interval = max_dynamic_interval

        if not self.path.exists():
            raise FileNotFoundError(f"Target path does not exist: {self.path}")
        if (
            not self.path.is_dir()
            and not self.path.resolve() == get_ram_dir() / self.name
        ):
            raise NotADirectoryError(f"{self.path} is not a directory")
        ensure_dir(self.backup_path)
