from pathlib import Path

import yaml
from xdg import BaseDirectory

from .log import log_info
from .target import Target


def load_config() -> list[Target]:
    CONFIG_FILE = Path(BaseDirectory.xdg_config_home) / "ramifier" / "config.yaml"
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")

    with CONFIG_FILE.open("r") as f_in:
        config_data = yaml.safe_load(f_in)

    targets = []
    for t in config_data.get("targets", []):
        target = Target(
            name=t["name"],
            path=t["path"],
            backup_path=t.get("backup_path"),
            interval=t.get("interval", 30),
            dynamic_interval=t.get("dynamic_interval", False),
            max_dynamic_interval=t.get("max_dynamic_interval", 100)
        )
        targets.append(target)
        log_info("Target added", target.name)
    return targets
