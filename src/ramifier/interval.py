from math import ceil, log
from threading import Thread
from time import sleep

from .log import log_info, log_warning
from .state import get_mtime_history, set_mtime_history_len
from .target import Target
from .utils import get_latest_mtime


class Interval:
    default_interval = 30
    default_min_interval = 5
    default_max_interval = 100
    default_mtime_history_len = 5

    def __init__(self, target: Target):
        self.target = target
        self.interval_dict = target.interval

        mtime_history_len = max(
            self.interval_dict.get("history_len", Interval.default_mtime_history_len), 1
        )
        set_mtime_history_len(self.target, mtime_history_len)

        self._smart_interval_thread = None

    def get_interval(self) -> int:
        mode = self.interval_dict.get("mode", "static")
        max_interval = self.interval_dict.get("max", Interval.default_max_interval)
        min_interval = self.interval_dict.get("min", Interval.default_min_interval)

        if mode == "static":
            return self.interval_dict.get("value", Interval.default_interval)

        elif mode == "dynamic":
            return self._dynamic_interval(max_interval, min_interval)

        elif mode == "smart":
            if self._smart_interval_thread is None:
                self._start_smart_interval(max_interval, min_interval)
                return self._dynamic_interval(max_interval, min_interval)
            else:
                return self.current_smart_interval

        else:
            raise ValueError(f"Unknown interval mode: {mode}")

    def _dynamic_interval(self, max_interval: int, min_interval: int) -> int:
        mtime_history = get_mtime_history(self.target)
        unique_count = len(set(mtime_history))
        dynamic_interval = (
            max_interval // unique_count if unique_count else min_interval
        )

        final_interval = max(min_interval, dynamic_interval)
        if final_interval != dynamic_interval:
            log_warning(
                f"Interval forced to {final_interval} minutes (was {dynamic_interval})",
                self.target.name,
            )
        else:
            log_info(f"Interval updated: {dynamic_interval} minutes", self.target.name)
        return final_interval

    def _start_smart_interval(self, max_interval: int, min_interval: int):
        self._smart_interval_thread = Thread(
            target=self._smart_interval,
            args=(max_interval, min_interval),
            daemon=True,
        )
        self._smart_interval_thread.start()

    def _smart_interval(self, max_interval: int, min_interval: int):
        just_started = True

        check_interval = max(min_interval // 2, (max_interval - min_interval) // 6, 1)
        current_mtime = get_latest_mtime(self.target.path)

        intensity = 1
        while True:
            new_mtime = get_latest_mtime(self.target.path)

            has_changes = new_mtime != current_mtime
            current_mtime = new_mtime

            if has_changes:
                intensity += 1
            else:
                decay = ceil(log(intensity)) if intensity > 1 else 0
                intensity = max(1, intensity - decay)

            self.current_smart_interval = int(
                max(max_interval / intensity, min_interval)
            )
            if not just_started:
                log_info(
                    f"Smart interval updated: {self.current_smart_interval} minutes (intensity={intensity})",
                    self.target.name,
                )
            else:
                just_started = False

            sleep(check_interval * 60)
