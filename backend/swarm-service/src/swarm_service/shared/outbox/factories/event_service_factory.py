from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from gateway.models.config.gateway_config import GatewayConfig
from gateway.service.events.event_service import EventService
from swarm_lifecycle.factories.factory import Factory
from swarm_storage.shared.postgres.postgres_pool import PostgresPool


class EventServiceFactory(Factory[EventService]):
    """Builds the event service of the gateway from its configuration.

    Attributes:
        config (GatewayConfig): The configuration of the gateway.
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

    def _build(self) -> EventService:
        """Build one closed event service, with its own pool.

        Returns:
            EventService: A new service.
        """
        self.logger.debug("Building an event service on schema %s.", self.config.schema_name)
        pool = PostgresPool(self.config.postgres)
        return EventService(pool, self.config.schema_name)
