from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
from fastapi import FastAPI

pytest.importorskip("swarm_core")

# First-party imports
from flight_engine.api.cli.commands.serve_command import ServeCommand  # isort: skip
from flight_engine.api.factories.command_factory import CommandFactory  # isort: skip
from flight_engine.api.factories.live.live_server_factory import LiveServerFactory  # isort: skip
from flight_engine.api.factories.serve.serve_command_factory import ServeCommandFactory  # isort: skip
from flight_engine.api.server.live_server import LiveServer  # isort: skip
from flight_engine.models.config.live_server_config import LiveServerConfig  # isort: skip
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory  # isort: skip
from swarm_lifecycle.factories.runnable_factory import RunnableFactory  # isort: skip


class TestFlightEngineApiFactories:
    CONFIG_NAME: ClassVar[str] = "app.yaml"
    STATUS_INTERVAL_S: ClassVar[float] = 0.5

    def test_the_serve_factory_builds_a_serve_command(self, tmp_path: Path) -> None:
        assert isinstance(ServeCommandFactory(tmp_path / self.CONFIG_NAME).create(), ServeCommand)

    def test_the_serve_factory_builds_a_new_command_on_each_call(self, tmp_path: Path) -> None:
        factory = ServeCommandFactory(tmp_path / self.CONFIG_NAME)

        assert factory.create() is not factory.create()

    def test_the_serve_factory_is_a_command_factory_and_a_runnable_factory(self, tmp_path: Path) -> None:
        factory = ServeCommandFactory(tmp_path / self.CONFIG_NAME)

        assert isinstance(factory, CommandFactory)
        assert isinstance(factory, RunnableFactory)

    def test_a_command_factory_cannot_be_instantiated(self) -> None:
        with pytest.raises(TypeError):
            CommandFactory()  # type: ignore[abstract]

    def test_the_live_server_factory_builds_a_live_server_with_the_configured_status_interval(self) -> None:
        config = LiveServerConfig(status_interval_s=self.STATUS_INTERVAL_S)

        server = LiveServerFactory(FastAPI(), config).create()

        assert isinstance(server, LiveServer)
        assert server.status_interval_s == self.STATUS_INTERVAL_S

    def test_the_live_server_factory_is_an_async_runnable_factory(self) -> None:
        assert isinstance(LiveServerFactory(FastAPI(), LiveServerConfig()), AsyncRunnableFactory)
