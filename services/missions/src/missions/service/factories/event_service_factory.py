from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from missions.models.config.missions_config import MissionsConfig
from missions.service.events.event_service import EventService
from swarm_lifecycle.factories.factory import Factory
from swarm_storage.shared.postgres.postgres_pool import PostgresPool


class EventServiceFactory(Factory[EventService]):
    """Builds event services, each on its own closed pool.

    Attributes:
        config (MissionsConfig): The settings the pool and the schema come from.
    """

    def __init__(self, config: MissionsConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the factory.

        Args:
            config (MissionsConfig): The settings the pool and the schema come from.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> EventService:
        """Build one service on a new pool, which the caller opens.

        Returns:
            EventService: A service for the schema of the configuration.
        """
        pool = PostgresPool(self.config.postgres)
        self.logger.debug("Built a pool for schema %s.", self.config.schema_name)
        return EventService(pool, self.config.schema_name)
