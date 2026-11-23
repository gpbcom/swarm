from __future__ import annotations

# Standard library imports
from importlib.metadata import version
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from gateway.models.config.gateway_config import GatewayConfig
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
        - **No resource is served yet**: the resources an Operator owns come with the verified token and later tickets.
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
            FastAPI: The application, with the REST conventions of Swarm and no router.
        """
        self.logger.debug("Building the gateway application.")
        return RestAppBuilder(self.config.rest).build(self.TITLE, version(self.DISTRIBUTION), routers=[])
