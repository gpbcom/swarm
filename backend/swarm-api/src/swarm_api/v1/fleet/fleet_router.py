from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import APIRouter, FastAPI

# First-party imports
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_api.middleware.idempotency_middleware import IdempotencyMiddleware
from swarm_models.config.fleet.fleet_config import FleetConfig
from swarm_service.shared.idempotency.factories.idempotency_service_factory import IdempotencyServiceFactory


class FleetRouter(APIRouter):
    """The ``/v1`` routes of the fleet domain, and the FastAPI application of the fleet app that serves them.

    Attributes:
        TITLE (ClassVar[str]): The title of the API.
        VERSION (ClassVar[str]): The version of the API.
        fleet_config (FleetConfig): The settings of the fleet app.
        logger (Logger): Logger instance.

    Notes:
        - No route is served yet: the routes of the fleet domain come with their own tickets.
        - **The published document is generated from this application**: run ``uv run swarm-openapi-export`` after
          any change to a route, because ``uv run swarm-openapi-check`` fails on a stale file.
    """

    TITLE: ClassVar[str] = "Swarm fleet"
    VERSION: ClassVar[str] = "0.1.0"

    def __init__(self, config: FleetConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the router.

        Args:
            config (FleetConfig): The settings of the fleet app.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.fleet_config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def application(self) -> FastAPI:
        """Build the application of the fleet app.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm and this router.
        """
        self.logger.debug("Building the fleet application.")
        app = ProblemHandlers().application(self.TITLE, self.VERSION, [self])
        app.add_middleware(IdempotencyMiddleware, service=IdempotencyServiceFactory(self.fleet_config.rest).create())
        self.logger.debug("The problem handlers and the idempotency middleware are installed.")
        return app
