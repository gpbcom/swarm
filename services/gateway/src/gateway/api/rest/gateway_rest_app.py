from __future__ import annotations

# Standard library imports
from importlib.metadata import version
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from gateway.api.live.live_feed_lifespan import LiveFeedLifespan
from gateway.api.live.live_router import LiveRouter
from gateway.api.rest.auth.access_installer import AccessInstaller
from gateway.models.config.gateway_config import GatewayConfig
from gateway.service.factories.live.live_feed_factory import LiveFeedFactory
from swarm_rest.api.rest.rest_app_builder import RestAppBuilder


class GatewayRestApp:
    """Builds the FastAPI application of the gateway, served under ``/v1``.

    Attributes:
        TITLE (ClassVar[str]): The title of the API.
        DISTRIBUTION (ClassVar[str]): The name of the distribution whose version is the version of the API.
        OPENAPI_OUTPUT (ClassVar[str]): The published OpenAPI document, relative to the repository root.
        config (GatewayConfig): The configuration of the gateway.
        logger (Logger): Logger instance.

    Notes:
        - **No resource is served yet**: the app has no ``/v1`` route, so none carries a ``RouteAccess`` yet.
          Each route added later takes ``Depends(RouteAccess([...]))`` with the roles of the security page.
    """

    TITLE: ClassVar[str] = "Swarm gateway"
    DISTRIBUTION: ClassVar[str] = "swarm-gateway"
    OPENAPI_OUTPUT: ClassVar[str] = "packages/ts/api-client/openapi/gateway.json"

    def __init__(self, config: GatewayConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the builder.

        Args:
            config (GatewayConfig): The configuration of the gateway.
            logger (Optional[Logger]): Logger instance.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def build(self) -> FastAPI:
        """Build the application.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm, the access check and the live socket.
        """
        self.logger.debug("Building the gateway application.")
        feed = LiveFeedFactory(self.config.live).create()
        app = RestAppBuilder(self.config.rest).build(self.TITLE, version(self.DISTRIBUTION), routers=[])
        app.include_router(LiveRouter(feed.source_for, self.config.live.session).build())
        app.router.lifespan_context = LiveFeedLifespan(feed).lifespan
        self.logger.debug("The live socket and its feed are wired on the gateway application.")
        AccessInstaller().install(app, self.config.auth)
        self.logger.debug("The access check is installed on the gateway application.")
        return app
