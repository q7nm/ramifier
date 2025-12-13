from .log import log_info
from .state import get_mtime_history, set_mtime_history_len
from .target import Target


class Interval:
    default_interval = 30
    default_min_dynamic_interval = 5
    default_max_dynamic_interval = 100
    default_mtime_history_len = 5

    def __init__(self, target: Target):
        self.target = target
        self.interval_dict = target.interval

        mtime_history_len = max(
            self.interval_dict.get("history_len", Interval.default_mtime_history_len), 1
        )
        set_mtime_history_len(self.target, mtime_history_len)

    def get_interval(self) -> int:
        mode = self.interval_dict.get("mode", "static")

        if mode == "static":
            return self.interval_dict.get("value", Interval.default_interval)
        elif mode == "dynamic":
            min_dynamic_interval = self.interval_dict.get(
                "min", Interval.default_min_dynamic_interval
            )
            max_dynamic_interval = self.interval_dict.get(
                "max", Interval.default_max_dynamic_interval
            )
            return self._dynamic_interval(max_dynamic_interval, min_dynamic_interval)
        else:
            raise ValueError(f"Unknown interval mode: {mode}")

    def _dynamic_interval(
        self, max_dynamic_interval: int, min_dynamic_interval: int
    ) -> int:
        mtime_history = get_mtime_history(self.target)
        unique_count = len(set(mtime_history))
        dynamic_interval = (
            max_dynamic_interval // unique_count
            if unique_count
            else min_dynamic_interval
        )

        final_interval = max(min_dynamic_interval, dynamic_interval)
        if final_interval != dynamic_interval:
            log_warning(
                f"Interval forced to {final_interval} minutes (was {dynamic_interval})",
                self.target.name,
            )
        else:
            log_info(f"Interval updated: {dynamic_interval} minutes", self.target.name)
        return final_interval
