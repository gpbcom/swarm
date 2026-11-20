from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import List, Optional
from uuid import UUID

# First-party imports
from swarm_models.models.events.event import Event
from swarm_storage.storage.postgres.postgres_pool import PostgresPool
from swarm_storage.storage.postgres.repositories.outbox_repository import OutboxRepository


class EventService:
    """Records the events of the gateway in its outbox, and reads the ones waiting to be published.

    Attributes:
        pool (PostgresPool): The pool the units of work come from.
        schema_name (str): The schema that holds the outbox.
        logger (Logger): Logger instance.

    Notes:
        - Each method opens one unit of work for the Operator it is given.
        - **Nothing here filters by Operator**: row-level security does, so a call without an Operator reads nothing.
    """

    def __init__(self, pool: PostgresPool, schema_name: str, logger: Optional[Logger] = None) -> None:
        """Prepare a closed service.

        Args:
            pool (PostgresPool): The pool the units of work come from.
            schema_name (str): The schema that holds the outbox.
            logger (Optional[Logger]): Logger instance.
        """
        self.pool = pool
        self.schema_name = schema_name
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def open(self) -> None:
        """Open the pool.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageConnectionError: If the database cannot be reached.
        """
        await self.pool.open()
        self.logger.info("Event service opened.")

    async def close(self) -> None:
        """Close the pool, safely before ``open`` and when called twice."""
        await self.pool.close()
        self.logger.info("Event service closed.")

    async def record(self, event: Event) -> Event:
        """Record one event in the outbox, in the transaction of the Operator that owns it.

        Args:
            event (Event): The event.

        Returns:
            Event: The event as stored.

        Raises:
            SEStorageNotOpenError: If the service is not open.
            SEStorageOperatorRefusedError: If row-level security refuses the write.
        """
        async with self.pool.unit_of_work(event.operator_id) as unit_of_work:
            stored = await OutboxRepository(unit_of_work, self.schema_name).add(event)
        self.logger.info("Recorded event %s.", event.id)
        return stored

    async def pending(
        self, operator_id: Optional[UUID], limit: int = OutboxRepository.PAGE_SIZE_DEFAULT
    ) -> List[Event]:
        """Read the events of one Operator that are not yet published.

        Args:
            operator_id (Optional[UUID]): The Operator, or none, which reads nothing.
            limit (int): The most events to read.

        Returns:
            List[Event]: The pending events of the Operator, in recording order.

        Raises:
            SEStorageNotOpenError: If the service is not open.
            SEStorageInvalidPageError: If the limit is outside the bounds.
        """
        async with self.pool.unit_of_work(operator_id) as unit_of_work:
            events = await OutboxRepository(unit_of_work, self.schema_name).pending(limit)
        self.logger.debug("Read %d pending events.", len(events))
        return events
