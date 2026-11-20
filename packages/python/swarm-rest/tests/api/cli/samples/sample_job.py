from __future__ import annotations

import asyncio

from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class SampleJob(AsyncRunnable):
    """A short job that records its calls and fails on demand."""

    WORK_S = 0.03
    FAILURE_MESSAGE = "The sample job failed."

    def __init__(self, fail: bool, status_interval_s: float) -> None:
        super().__init__(status_interval_s)
        self.fail = fail
        self.initialized = False
        self.ran = False
        self.closed = False

    async def initialize(self) -> None:
        self.initialized = True

    async def run(self) -> None:
        await asyncio.sleep(self.WORK_S)
        self.ran = True
        if self.fail:
            raise RuntimeError(self.FAILURE_MESSAGE)

    async def close(self) -> None:
        self.closed = True
