from __future__ import annotations

import asyncio
import logging
from logging import Logger, getLogger
from typing import Awaitable, Callable, Dict

import pytest
from lifecycle_recording_async_runnable import RecordingAsyncRunnable

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

    async def test_execute_calls_initialize_run_close_in_order(self) -> None:
        runnable = RecordingAsyncRunnable()
        await runnable.execute()
        assert runnable.calls == ["initialize", "run", "close"]

    async def test_a_failing_initialize_skips_run_and_still_closes(self) -> None:
        runnable = RecordingAsyncRunnable(fail_in="initialize")
        with pytest.raises(RuntimeError, match="Failure in initialize."):
            await runnable.execute()
        assert runnable.calls == ["initialize", "close"]

    async def test_a_failing_run_still_closes(self) -> None:
        runnable = RecordingAsyncRunnable(fail_in="run")
        with pytest.raises(RuntimeError, match="Failure in run."):
            await runnable.execute()
        assert runnable.calls == ["initialize", "run", "close"]

    async def test_a_failing_close_propagates_after_run(self) -> None:
        runnable = RecordingAsyncRunnable(fail_in="close")
        with pytest.raises(RuntimeError, match="Failure in close."):
            await runnable.execute()
        assert runnable.calls == ["initialize", "run", "close"]

    async def test_success_logs_info_with_the_class_name(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.DEBUG):
            await RecordingAsyncRunnable().execute()
        records = [record for record in caplog.records if record.levelno == logging.INFO]
        assert any("RecordingAsyncRunnable" in record.getMessage() for record in records)

    @pytest.mark.parametrize("fail_in", ["initialize", "run"])
    async def test_failure_logs_error_with_the_class_name(self, fail_in: str, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.DEBUG), pytest.raises(RuntimeError):
            await RecordingAsyncRunnable(fail_in=fail_in).execute()
        records = [record for record in caplog.records if record.levelno == logging.ERROR]
        assert any("RecordingAsyncRunnable" in record.getMessage() for record in records)

    async def test_a_given_logger_is_used(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = getLogger("given.async_runnable.logger")
        runnable = RecordingAsyncRunnable(logger=logger)
        assert runnable.logger is logger
        with caplog.at_level(logging.DEBUG, logger=logger.name):
            await runnable.execute()
        assert any(record.name == logger.name for record in caplog.records)

    def test_the_default_logger_is_a_logger(self) -> None:
        assert isinstance(RecordingAsyncRunnable().logger, Logger)

    async def test_a_long_run_reports_its_status_at_each_interval(self, caplog: pytest.LogCaptureFixture) -> None:
        runnable = RecordingAsyncRunnable(run_for_s=0.25, status_interval_s=0.05)
        with caplog.at_level(logging.INFO):
            await runnable.execute()
        reports = [record for record in caplog.records if record.getMessage().startswith("Status of ")]
        assert len(reports) >= 3
        assert all(record.levelno == logging.INFO for record in reports)
        assert all("RecordingAsyncRunnable" in record.getMessage() for record in reports)

    async def test_the_last_status_is_logged_before_close(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.INFO):
            await RecordingAsyncRunnable().execute()
        last = [record.getMessage() for record in caplog.records if record.getMessage().startswith("Last status of ")]
        assert last == ["Last status of RecordingAsyncRunnable: 2 lifecycle calls so far."]

    @pytest.mark.parametrize("fail_in", ["initialize", "run"])
    async def test_a_failing_task_still_logs_its_last_status(
        self, fail_in: str, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.INFO), pytest.raises(RuntimeError):
            await RecordingAsyncRunnable(fail_in=fail_in).execute()
        assert any(record.getMessage().startswith("Last status of ") for record in caplog.records)

    async def test_no_status_report_is_left_running_after_execute(self) -> None:
        await RecordingAsyncRunnable(status_interval_s=0.01).execute()
        await asyncio.sleep(0.03)
        running = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
        assert running == []

    @pytest.mark.parametrize("value", [0, -1.0, True, "60"])
    def test_a_status_interval_that_is_not_a_positive_number_is_refused(self, value: float) -> None:
        with pytest.raises(SEAsyncRunnableInvalidStatusIntervalError):
            RecordingAsyncRunnable(status_interval_s=value)
