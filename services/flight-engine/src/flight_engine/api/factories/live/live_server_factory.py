from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from flight_engine.api.server.live_server import LiveServer
from flight_engine.models.config.live_server_config import LiveServerConfig
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory


class LiveServerFactory(AsyncRunnableFactory[LiveServer]):
    """Factory of the server of the local live socket.

    Attributes:
        app (FastAPI): The application to serve.
        config (LiveServerConfig): The host, the port and the status interval.
        logger (Logger): Logger instance.
    """

    def __init__(self, app: FastAPI, config: LiveServerConfig, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            app (FastAPI): The application to serve.
            config (LiveServerConfig): The host, the port and the status interval.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.app = app
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> LiveServer:
        """Build one live server, not yet listening.

        Returns:
            LiveServer: A new server.
        """
        self.logger.debug("Building a live server for port %d.", self.config.port)
        return LiveServer(self.app, self.config)
