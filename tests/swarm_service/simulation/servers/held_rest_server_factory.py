from __future__ import annotations

# Standard library imports
from typing import List

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_web.factories.rest_server_factory import RestServerFactory
from swarm_web.models.config.rest_config import RestConfig
from swarm_web.rest.rest_server import RestServer


class HeldRestServerFactory(RestServerFactory):
    """Builds real REST servers and keeps each one, so that a test can end the server it built."""

    def __init__(self, app: FastAPI, config: RestConfig) -> None:
        super().__init__(app, config)
        self.built: List[RestServer] = []

    def _build(self) -> RestServer:
        server = super()._build()
        self.built.append(server)
        return server
