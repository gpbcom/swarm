from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_clients.gateway.keycloak.keycloak_admin_client import KeycloakAdminClient
from swarm_lifecycle.factories.factory import Factory
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_service.gateway.operators.operator_service import OperatorService
from swarm_storage.shared.postgres.postgres_pool import PostgresPool


class OperatorServiceFactory(Factory[OperatorService]):
    """Builds the Operator service of the gateway from its configuration.

    Attributes:
        config (GatewayConfig): The configuration of the gateway.
        logger (Logger): Logger instance.

    Notes:
        - **Nothing is opened and no secret is read here**: the pool opens on the first call of the service.
    """

    def __init__(self, config: GatewayConfig, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            config (GatewayConfig): The configuration of the gateway.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> OperatorService:
        """Build one service on its own pool and Keycloak client, nothing opened.

        Returns:
            OperatorService: A new service.
        """
        self.logger.debug("Building the Operator service.")
        return OperatorService(
            PostgresPool(self.config.postgres),
            self.config.schema_name,
            self.config.operators.cell,
            KeycloakAdminClient(self.config.operators.keycloak),
        )
