from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_lifecycle.factories.factory import Factory
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_service.shared.outbox.event_service import EventService
from swarm_storage.shared.postgres.postgres_pool import PostgresPool


class EventServiceFactory(Factory[EventService]):
    """Builds the event service of an app from its PostgreSQL settings.

    Attributes:
        postgres (PostgresConfig): The connection pool settings of the app.
        schema_name (str): The schema that holds the outbox of the app.
    """

    def __init__(self, postgres: PostgresConfig, schema_name: str, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            postgres (PostgresConfig): The connection pool settings of the app.
            schema_name (str): The schema that holds the outbox of the app.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.postgres = postgres
        self.schema_name = schema_name

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> EventService:
        """Build one closed event service, with its own pool.

        Returns:
            EventService: A new service.
        """
        self.logger.debug("Building an event service on schema %s.", self.schema_name)
        pool = PostgresPool(self.postgres)
        return EventService(pool, self.schema_name)
