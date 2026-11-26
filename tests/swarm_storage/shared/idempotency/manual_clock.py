from __future__ import annotations


class ManualClock:
    """A clock that only moves when a test advances it.

    Attributes:
        now_s (float): The current time, in seconds.
    """

    def __init__(self, now_s: float = 0.0) -> None:
        self.now_s = now_s

    def advance(self, seconds: float) -> None:
        self.now_s += seconds

    def __call__(self) -> float:
        return self.now_s
