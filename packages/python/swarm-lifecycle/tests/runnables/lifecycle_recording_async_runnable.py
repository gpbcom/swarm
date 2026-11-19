from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger
from typing import ClassVar, List, Optional

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class RecordingAsyncRunnable(AsyncRunnable):
    """Stand-in async runnable that records the lifecycle methods called, and can fail in one of them."""

    STATUS_INTERVAL_S: ClassVar[float] = 60.0

    def __init__(
        self,
        fail_in: Optional[str] = None,
        run_for_s: float = 0.0,
        status_interval_s: float = STATUS_INTERVAL_S,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(status_interval_s, logger)
        self.fail_in = fail_in
        self.run_for_s = run_for_s
        self.calls: List[str] = []

    def record(self, name: str) -> None:
        self.calls.append(name)
        if self.fail_in == name:
            raise RuntimeError(f"Failure in {name}.")

    async def initialize(self) -> None:
        self.record("initialize")

    async def run(self) -> None:
        self.record("run")
        await asyncio.sleep(self.run_for_s)

    async def close(self) -> None:
        self.record("close")

    def status(self) -> str:
        return f"{len(self.calls)} lifecycle calls so far."
