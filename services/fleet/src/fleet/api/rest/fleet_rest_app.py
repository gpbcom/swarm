from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from fleet.models.config.fleet_config import FleetConfig
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_api.middleware.idempotency_middleware import IdempotencyMiddleware
from swarm_models.rest.problems.problem import Problem
from swarm_service.shared.idempotency.factories.idempotency_service_factory import IdempotencyServiceFactory
from swarm_web.rest.rest_app_builder import RestAppBuilder


class FleetRestApp:
    """The REST application of the fleet service, served under ``/v1``.

    Attributes:
        TITLE (str): The title of the API.
        VERSION (str): The version of the API.
        OPENAPI_OUTPUT (str): The published OpenAPI document, relative to the repository root.
        config (FleetConfig): The settings of the service.
        logger (Logger): Logger instance.

    Notes:
        - No router is added yet: the routes of the fleet come with their own tickets.
        - ``frontend/packages/api-client`` is generated from the published document.
    """

    TITLE: ClassVar[str] = "Swarm fleet"
    VERSION: ClassVar[str] = "0.1.0"
    OPENAPI_OUTPUT: ClassVar[str] = "frontend/packages/api-client/openapi/fleet.json"

    def __init__(self, config: FleetConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the application.

        Args:
            config (FleetConfig): The settings of the service.
            logger (Optional[Logger]): Logger instance.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def build(self) -> FastAPI:
        """Build the FastAPI application.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm and no router.
        """
        self.logger.debug("Building the fleet application.")
        app = RestAppBuilder().build(self.TITLE, self.VERSION, [], Problem, Problem.MEDIA_TYPE)
        ProblemHandlers().install(app)
        app.add_middleware(IdempotencyMiddleware, service=IdempotencyServiceFactory(self.config.rest).create())
        self.logger.debug("The problem handlers and the idempotency middleware are installed.")
        return app
