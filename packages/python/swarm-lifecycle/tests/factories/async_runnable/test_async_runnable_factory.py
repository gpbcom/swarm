from __future__ import annotations

from logging import DEBUG, Logger, getLogger

import pytest
from lifecycle_sample_async_runnable import SampleAsyncRunnable
from lifecycle_sample_async_runnable_factory import SampleAsyncRunnableFactory

from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_lifecycle.factories.factory import Factory
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class TestAsyncRunnableFactory:
    @pytest.mark.parametrize("factory_class", [Factory, AsyncRunnableFactory])
    def test_an_abstract_factory_cannot_be_instantiated(self, factory_class: type[Factory[AsyncRunnable]]) -> None:
        with pytest.raises(TypeError):
            factory_class()

    def test_the_factory_is_a_factory(self) -> None:
        assert issubclass(SampleAsyncRunnableFactory, Factory)

    def test_create_returns_the_sample(self) -> None:
        assert isinstance(SampleAsyncRunnableFactory().create(), SampleAsyncRunnable)

    def test_create_returns_a_new_one_each_time(self) -> None:
        factory = SampleAsyncRunnableFactory()
        assert factory.create() is not factory.create()

    async def test_the_created_async_runnable_executes(self) -> None:
        sample = SampleAsyncRunnableFactory().create()
        assert sample.executed is False
        statuses = [status async for status in sample.execute()]
        assert sample.executed is True
        assert statuses[-1] is RunnableStatus.EXECUTED

    def test_create_logs_the_product_class(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(DEBUG):
            SampleAsyncRunnableFactory().create()
        assert any(r.levelno == DEBUG and "SampleAsyncRunnable" in r.getMessage() for r in caplog.records)

    def test_a_given_logger_is_used(self, caplog: pytest.LogCaptureFixture) -> None:
        logger: Logger = getLogger("tests.given_logger_async_runnable")
        with caplog.at_level(DEBUG, logger=logger.name):
            SampleAsyncRunnableFactory(logger).create()
        assert [r.name for r in caplog.records if "SampleAsyncRunnable" in r.getMessage()] == [logger.name]
