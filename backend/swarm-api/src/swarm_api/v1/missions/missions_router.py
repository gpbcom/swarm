from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import APIRouter, FastAPI

# First-party imports
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_api.middleware.idempotency_middleware import IdempotencyMiddleware
from swarm_models.config.missions.missions_config import MissionsConfig
from swarm_service.shared.idempotency.factories.idempotency_service_factory import IdempotencyServiceFactory


class MissionsRouter(APIRouter):
    """The ``/v1`` routes of the missions domain, and the FastAPI application of the missions app that serves them.

    Attributes:
        TITLE (ClassVar[str]): The title of the API.
        VERSION (ClassVar[str]): The version of the API.
        missions_config (MissionsConfig): The settings of the missions app.
        logger (Logger): Logger instance.

    Notes:
        - No route is served yet: the routes of the missions domain come with their own tickets.
        - **The published document is generated from this application**: run ``uv run swarm-openapi-export`` after
          any change to a route, because ``uv run swarm-openapi-check`` fails on a stale file.
    """

    TITLE: ClassVar[str] = "Swarm missions"
    VERSION: ClassVar[str] = "0.1.0"

    def __init__(self, config: MissionsConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the router.

        Args:
            config (MissionsConfig): The settings of the missions app.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.missions_config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def application(self) -> FastAPI:
        """Build the application of the missions app.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm and this router.
        """
        self.logger.debug("Building the missions application.")
        app = ProblemHandlers().application(self.TITLE, self.VERSION, [self])
        app.add_middleware(IdempotencyMiddleware, service=IdempotencyServiceFactory(self.missions_config.rest).create())
        self.logger.debug("The problem handlers and the idempotency middleware are installed.")
        return app
