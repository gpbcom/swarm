from __future__ import annotations

# First-party imports
from swarm_lifecycle.factories.runnable_factory import RunnableFactory
from swarm_web.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory
from swarm_web.runners.async_runnable_runner import AsyncRunnableRunner
from tests.swarm_web.runners.sample_job import SampleJob


class TestAsyncRunnableRunnerFactory:
    def test_create_returns_a_new_runner_built_from_the_arguments(self) -> None:
        job = SampleJob(fail=False, status_interval_s=0.01)
        factory = AsyncRunnableRunnerFactory(job)
        assert isinstance(factory, RunnableFactory)
        first = factory.create()
        second = factory.create()
        assert isinstance(first, AsyncRunnableRunner)
        assert first is not second
        assert first.runnable is job
