from __future__ import annotations

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_rest.api.factories.rest_server_factory import RestServerFactory
from swarm_rest.api.rest.rest_server import RestServer
from swarm_rest.models.config.rest_config import RestConfig


class TestRestServerFactory:
    def test_create_returns_a_new_server_built_from_the_arguments(self) -> None:
        app = FastAPI()
        config = RestConfig()
        factory = RestServerFactory(app, config)
        assert isinstance(factory, AsyncRunnableFactory)
        first = factory.create()
        second = factory.create()
        assert isinstance(first, RestServer)
        assert first is not second
        assert first.app is app
        assert first.config is config
        assert first.status_interval_s == config.status_interval_s
