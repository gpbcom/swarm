from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_web.models.config.rest_config import RestConfig
from swarm_web.rest.rest_server import RestServer


class RestServerFactory(AsyncRunnableFactory[RestServer]):
    """Builds REST servers.

    Attributes:
        app (FastAPI): The application each server serves.
        config (RestConfig): The settings of each server.
    """

    def __init__(self, app: FastAPI, config: RestConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            app (FastAPI): The application each server serves.
            config (RestConfig): The settings of each server.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.app = app
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> RestServer:
        """Build one server.

        Returns:
            RestServer: A new server of the application.
        """
        self.logger.debug("Building a server on port %d.", self.config.port)
        return RestServer(self.app, self.config)
