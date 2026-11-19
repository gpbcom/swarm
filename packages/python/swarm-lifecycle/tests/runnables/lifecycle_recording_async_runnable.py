from __future__ import annotations

# Standard library imports
from logging import Logger
from typing import List, Optional

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class RecordingAsyncRunnable(AsyncRunnable):
    """Stand-in async runnable that records the lifecycle methods called, and can fail in one of them."""

    def __init__(self, fail_in: Optional[str] = None, logger: Optional[Logger] = None) -> None:
        super().__init__(logger)
        self.fail_in = fail_in
        self.calls: List[str] = []

    def record(self, name: str) -> None:
        self.calls.append(name)
        if self.fail_in == name:
            raise RuntimeError(f"Failure in {name}.")

    async def initialize(self) -> None:
        self.record("initialize")

    async def run(self) -> None:
        self.record("run")

    async def close(self) -> None:
        self.record("close")
