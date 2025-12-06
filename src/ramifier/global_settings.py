import os
from pathlib import Path

from .utils import ensure_dir, get_ram_dir


class GlobalSettings:
    def __init__(
        self,
        max_backups: int,
        interval: int,
        dynamic_interval: bool,
        max_dynamic_interval: int,
        compression_level: int,
        compression_threads: int,
        ram_dir: str,
    ):
        self.max_backups = max_backups
        self.interval = interval
        self.dynamic_interval = dynamic_interval
        self.max_dynamic_interval = max_dynamic_interval
        self.compression_level = compression_level
        self.compression_threads = compression_threads
        if ram_dir is None:
            self.ram_dir = get_ram_dir()
        else:
            ram_dir = Path(os.path.expandvars(ram_dir)).expanduser()
            ensure_dir(ram_dir, 0o700)
            self.ram_dir = ram_dir
