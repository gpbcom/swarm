from __future__ import annotations

from logging import DEBUG, Logger, getLogger

import pytest
from lifecycle_sample_runnable import SampleRunnable
from lifecycle_sample_runnable_factory import SampleRunnableFactory

from swarm_lifecycle.factories.factory import Factory
from swarm_lifecycle.factories.runnable_factory import RunnableFactory


class TestRunnableFactory:
    @pytest.mark.parametrize("factory_class", [Factory, RunnableFactory])
    def test_an_abstract_factory_cannot_be_instantiated(self, factory_class: type[Factory[object]]) -> None:
        with pytest.raises(TypeError):
            factory_class()

    def test_the_factory_is_a_factory(self) -> None:
        assert issubclass(SampleRunnableFactory, Factory)

    def test_create_returns_the_sample(self) -> None:
        assert isinstance(SampleRunnableFactory().create(), SampleRunnable)

    def test_create_returns_a_new_one_each_time(self) -> None:
        factory = SampleRunnableFactory()
        assert factory.create() is not factory.create()

    def test_the_created_runnable_executes(self) -> None:
        sample = SampleRunnableFactory().create()
        assert sample.executed is False
        sample.execute()
        assert sample.executed is True

    def test_create_logs_the_product_class(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(DEBUG):
            SampleRunnableFactory().create()
        assert any(r.levelno == DEBUG and "SampleRunnable" in r.getMessage() for r in caplog.records)

    def test_a_given_logger_is_used(self, caplog: pytest.LogCaptureFixture) -> None:
        logger: Logger = getLogger("tests.given_logger_runnable")
        with caplog.at_level(DEBUG, logger=logger.name):
            SampleRunnableFactory(logger).create()
        assert [r.name for r in caplog.records if "SampleRunnable" in r.getMessage()] == [logger.name]
