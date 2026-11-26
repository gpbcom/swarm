from __future__ import annotations

# Standard library imports
from importlib.metadata import version
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import APIRouter, FastAPI

# First-party imports
from swarm_api.handlers.access_handlers import AccessHandlers
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_api.middleware.idempotency_middleware import IdempotencyMiddleware
from swarm_api.v1.live.live_router import LiveRouter
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_service.gateway.factories.live.live_feed_factory import LiveFeedFactory
from swarm_service.gateway.live.live_feed_lifespan import LiveFeedLifespan
from swarm_service.shared.idempotency.factories.idempotency_service_factory import IdempotencyServiceFactory


class GatewayRouter(APIRouter):
    """The ``/v1`` routes of the gateway, and the FastAPI application of the gateway app that serves them.

    Attributes:
        TITLE (ClassVar[str]): The title of the API.
        DISTRIBUTION (ClassVar[str]): The name of the distribution whose version is the version of the API.
        gateway_config (GatewayConfig): The configuration of the gateway.
        logger (Logger): Logger instance.

    Notes:
        - **No resource is served yet**: the router has no ``/v1`` route, so none carries a ``RouteAccess`` yet.
          Each route added later takes ``Depends(RouteAccess([...]))`` with the roles of the security page.
        - ``application`` is the one place that wires the gateway, so that its app and the OpenAPI script build the
          same application.
    """

    TITLE: ClassVar[str] = "Swarm gateway"
    DISTRIBUTION: ClassVar[str] = "swarm-gateway"

    def __init__(self, config: GatewayConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the router.

        Args:
            config (GatewayConfig): The configuration of the gateway.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.gateway_config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def application(self) -> FastAPI:
        """Build the application of the gateway.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm, the access check and the live socket.
        """
        self.logger.debug("Building the gateway application.")
        feed = LiveFeedFactory(self.gateway_config.live).create()
        app = ProblemHandlers().application(self.TITLE, version(self.DISTRIBUTION), [self])
        app.add_middleware(IdempotencyMiddleware, service=IdempotencyServiceFactory(self.gateway_config.rest).create())
        self.logger.debug("The problem handlers and the idempotency middleware are installed.")
        app.include_router(LiveRouter(feed.source_for, self.gateway_config.live.session))
        app.router.lifespan_context = LiveFeedLifespan(feed).lifespan
        self.logger.debug("The live socket and its feed are wired on the gateway application.")
        AccessHandlers().install(app, self.gateway_config.auth)
        self.logger.debug("The access check is installed on the gateway application.")
        return app
