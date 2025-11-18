from .log import log_info
from .state import STATE
from .target import Target


def dynamic_interval(target: Target) -> int:
    mtime_history = STATE["targets"].get(target.name, {}).get("mtime_history", [])
    unique_count = len(set(mtime_history))
    interval = (
        target.max_dynamic_interval // unique_count if unique_count else target.interval
    )
    log_info(f"Interval updated: {interval} minutes", target.name)
    return interval
