from __future__ import annotations

import asyncio
import logging
from logging import Logger, getLogger
from typing import Awaitable, Callable, Dict, List

import pytest
from lifecycle_recording_async_runnable import RecordingAsyncRunnable

from swarm_lifecycle.models.enums import RunnableStatus
from swarm_lifecycle.models.exceptions import SEAsyncRunnableInvalidStatusIntervalError
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class TestAsyncRunnable:
    def test_the_base_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            AsyncRunnable()  # type: ignore[abstract]

    @pytest.mark.parametrize("missing", ["initialize", "run", "close"])
    def test_a_subclass_missing_a_method_cannot_be_instantiated(self, missing: str) -> None:
        namespace: Dict[str, Callable[[AsyncRunnable], Awaitable[None]]] = {
            name: getattr(RecordingAsyncRunnable, name) for name in ("initialize", "run", "close") if name != missing
        }
        partial = type("PartialAsyncRunnable", (AsyncRunnable,), namespace)
        with pytest.raises(TypeError):
            partial()

    async def statuses(self, runnable: RecordingAsyncRunnable) -> List[RunnableStatus]:
        return [status async for status in runnable.execute()]

    async def test_execute_calls_initialize_run_close_in_order(self) -> None:
        runnable = RecordingAsyncRunnable()
        await self.statuses(runnable)
        assert runnable.calls == ["initialize", "run", "close"]

    async def test_a_failing_initialize_skips_run_and_still_closes(self) -> None:
        runnable = RecordingAsyncRunnable(fail_in="initialize")
        with pytest.raises(RuntimeError, match="Failure in initialize."):
            await self.statuses(runnable)
        assert runnable.calls == ["initialize", "close"]

    async def test_a_failing_run_still_closes(self) -> None:
        runnable = RecordingAsyncRunnable(fail_in="run")
        with pytest.raises(RuntimeError, match="Failure in run."):
            await self.statuses(runnable)
        assert runnable.calls == ["initialize", "run", "close"]

    async def test_a_failing_close_propagates_after_run(self) -> None:
        runnable = RecordingAsyncRunnable(fail_in="close")
        with pytest.raises(RuntimeError, match="Failure in close."):
            await self.statuses(runnable)
        assert runnable.calls == ["initialize", "run", "close"]

    async def test_a_runnable_starts_not_started(self) -> None:
        assert RecordingAsyncRunnable().status is RunnableStatus.NOT_STARTED

    async def test_a_quick_task_yields_only_executed(self) -> None:
        runnable = RecordingAsyncRunnable()
        assert await self.statuses(runnable) == [RunnableStatus.EXECUTED]
        assert runnable.status is RunnableStatus.EXECUTED

    async def test_a_long_run_yields_running_at_each_interval_then_executed(self) -> None:
        statuses = await self.statuses(RecordingAsyncRunnable(run_for_s=0.25, status_interval_s=0.05))
        assert len(statuses) >= 3
        assert set(statuses[:-1]) == {RunnableStatus.RUNNING}
        assert statuses[-1] is RunnableStatus.EXECUTED

    async def test_a_long_initialize_yields_initialising(self) -> None:
        statuses = await self.statuses(RecordingAsyncRunnable(initialize_for_s=0.15, status_interval_s=0.05))
        assert statuses[0] is RunnableStatus.INITIALISING

    async def test_every_status_yielded_is_a_runnable_status(self) -> None:
        statuses = await self.statuses(RecordingAsyncRunnable(run_for_s=0.12, status_interval_s=0.05))
        assert all(isinstance(status, RunnableStatus) for status in statuses)

    async def test_each_status_is_also_logged_at_info_with_the_time_elapsed(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO):
            statuses = await self.statuses(RecordingAsyncRunnable(run_for_s=0.12, status_interval_s=0.05))
        logged = [record.getMessage() for record in caplog.records if record.getMessage().startswith("Status of ")]
        assert len(logged) == len(statuses) - 1
        assert all(
            line.startswith(f"Status of RecordingAsyncRunnable: {RunnableStatus.RUNNING} after ") for line in logged
        )

    async def test_stopping_reading_cancels_the_work_and_still_closes(self) -> None:
        runnable = RecordingAsyncRunnable(run_for_s=10.0, status_interval_s=0.02)
        statuses = runnable.execute()
        first = await anext(statuses)
        await statuses.aclose()
        assert first is RunnableStatus.RUNNING
        assert runnable.calls == ["initialize", "run", "close"]

    async def test_no_task_is_left_running_after_execute(self) -> None:
        await self.statuses(RecordingAsyncRunnable(run_for_s=0.05, status_interval_s=0.01))
        running = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        assert running == []

    async def test_success_logs_info_with_the_class_name(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.DEBUG):
            await self.statuses(RecordingAsyncRunnable())
        records = [record for record in caplog.records if record.levelno == logging.INFO]
        assert any("RecordingAsyncRunnable" in record.getMessage() for record in records)

    @pytest.mark.parametrize("fail_in", ["initialize", "run"])
    async def test_failure_logs_error_with_the_class_name(self, fail_in: str, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.DEBUG), pytest.raises(RuntimeError):
            await self.statuses(RecordingAsyncRunnable(fail_in=fail_in))
        records = [record for record in caplog.records if record.levelno == logging.ERROR]
        assert any("RecordingAsyncRunnable" in record.getMessage() for record in records)

    async def test_a_given_logger_is_used(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = getLogger("given.async_runnable.logger")
        runnable = RecordingAsyncRunnable(logger=logger)
        assert runnable.logger is logger
        with caplog.at_level(logging.DEBUG, logger=logger.name):
            await self.statuses(runnable)
        assert any(record.name == logger.name for record in caplog.records)

    def test_the_default_logger_is_a_logger(self) -> None:
        assert isinstance(RecordingAsyncRunnable().logger, Logger)

    @pytest.mark.parametrize("value", [0, -1.0, True, "60"])
    def test_a_status_interval_that_is_not_a_positive_number_is_refused(self, value: float) -> None:
        with pytest.raises(SEAsyncRunnableInvalidStatusIntervalError):
            RecordingAsyncRunnable(status_interval_s=value)
