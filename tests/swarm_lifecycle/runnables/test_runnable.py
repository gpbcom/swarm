from __future__ import annotations

# Standard library imports
import logging
from logging import Logger, getLogger
from typing import Callable, Dict

# Third-party imports
import pytest
from lifecycle_recording_runnable import RecordingRunnable

# First-party imports
from swarm_lifecycle.runnables.runnable import Runnable


class TestRunnable:
    def test_the_base_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            Runnable()  # type: ignore[abstract]

    @pytest.mark.parametrize("missing", ["initialize", "run", "close"])
    def test_a_subclass_missing_a_method_cannot_be_instantiated(self, missing: str) -> None:
        namespace: Dict[str, Callable[[Runnable], None]] = {
            name: getattr(RecordingRunnable, name) for name in ("initialize", "run", "close") if name != missing
        }
        partial = type("PartialRunnable", (Runnable,), namespace)
        with pytest.raises(TypeError):
            partial()

    def test_execute_calls_initialize_run_close_in_order(self) -> None:
        runnable = RecordingRunnable()
        runnable.execute()
        assert runnable.calls == ["initialize", "run", "close"]

    def test_a_failing_initialize_skips_run_and_still_closes(self) -> None:
        runnable = RecordingRunnable(fail_in="initialize")
        with pytest.raises(RuntimeError, match="Failure in initialize."):
            runnable.execute()
        assert runnable.calls == ["initialize", "close"]

    def test_a_failing_run_still_closes(self) -> None:
        runnable = RecordingRunnable(fail_in="run")
        with pytest.raises(RuntimeError, match="Failure in run."):
            runnable.execute()
        assert runnable.calls == ["initialize", "run", "close"]

    def test_a_failing_close_propagates_after_run(self) -> None:
        runnable = RecordingRunnable(fail_in="close")
        with pytest.raises(RuntimeError, match="Failure in close."):
            runnable.execute()
        assert runnable.calls == ["initialize", "run", "close"]

    def test_success_logs_info_with_the_class_name(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.DEBUG):
            RecordingRunnable().execute()
        records = [record for record in caplog.records if record.levelno == logging.INFO]
        assert any("RecordingRunnable" in record.getMessage() for record in records)

    @pytest.mark.parametrize("fail_in", ["initialize", "run"])
    def test_failure_logs_error_with_the_class_name(self, fail_in: str, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.DEBUG), pytest.raises(RuntimeError):
            RecordingRunnable(fail_in=fail_in).execute()
        records = [record for record in caplog.records if record.levelno == logging.ERROR]
        assert any("RecordingRunnable" in record.getMessage() for record in records)

    def test_a_given_logger_is_used(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = getLogger("given.runnable.logger")
        runnable = RecordingRunnable(logger=logger)
        assert runnable.logger is logger
        with caplog.at_level(logging.DEBUG, logger=logger.name):
            runnable.execute()
        assert any(record.name == logger.name for record in caplog.records)

    def test_the_default_logger_is_a_logger(self) -> None:
        assert isinstance(RecordingRunnable().logger, Logger)
