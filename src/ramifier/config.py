from pathlib import Path

import yaml
from xdg import BaseDirectory

from .global_settings import GlobalSettings
from .log import log_info
from .target import Target

CONFIG_FILE = Path(BaseDirectory.xdg_config_home) / "ramifier" / "config.yaml"
if not CONFIG_FILE.exists():
    raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

with CONFIG_FILE.open("r") as f_in:
    CONFIG_DATA = yaml.safe_load(f_in)


def load_global_settings() -> GlobalSettings:
    s = CONFIG_DATA.get("global_settings", {})
    global_settings = GlobalSettings(
        ram_dir=s.get("ram_dir"),
        max_backups=s.get("max_backups", 3),
        interval=s.get("interval", {}),
        compression_level=s.get("compression_level", 3),
        compression_threads=s.get("compression_threads", 0),
    )
    return global_settings


def load_targets(global_settings: GlobalSettings) -> list[Target]:
    targets = []
    for t in CONFIG_DATA.get("targets", []):
        name = t.get("name")
        target = Target(
            name=name,
            path=t.get("path"),
            backup_path=t.get("backup_path"),
            max_backups=t.get("max_backups", global_settings.max_backups),
            interval=t.get("interval", global_settings.interval),
            compression_level=t.get(
                "compression_level", global_settings.compression_level
            ),
            compression_threads=t.get(
                "compression_threads", global_settings.compression_threads
            ),
            ram_path=global_settings.ram_dir / name,
        )
        if name in [t.name for t in targets]:
            raise RuntimeError(f"Target with name {name} already exists")

        targets.append(target)
        log_info("Target added", target.name)
    return targets
