from __future__ import annotations

import pytest
from samples.sample_job import SampleJob

from swarm_lifecycle.models.enums import RunnableStatus
from swarm_rest.api.cli.async_runnable_runner import AsyncRunnableRunner


class TestAsyncRunnableRunner:
    STATUS_INTERVAL_S = 0.01

    def test_execute_ends_with_the_executed_status_and_closes_the_job(self) -> None:
        job = SampleJob(fail=False, status_interval_s=self.STATUS_INTERVAL_S)
        runner = AsyncRunnableRunner(job)
        runner.execute()
        assert runner.last_status == RunnableStatus.EXECUTED
        assert job.initialized
        assert job.closed

    def test_a_failing_job_propagates_its_error_and_is_closed(self) -> None:
        job = SampleJob(fail=True, status_interval_s=self.STATUS_INTERVAL_S)
        runner = AsyncRunnableRunner(job)
        with pytest.raises(RuntimeError, match=SampleJob.FAILURE_MESSAGE):
            runner.execute()
        assert job.closed
