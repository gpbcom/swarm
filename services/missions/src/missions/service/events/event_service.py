from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import List, Optional
from uuid import UUID

# First-party imports
from swarm_models.events.event import Event
from swarm_storage.shared.postgres.postgres_pool import PostgresPool
from swarm_storage.shared.postgres.repositories.outbox_repository import OutboxRepository


class EventService:
    """Records the events of missions in the outbox and reads the ones still pending.

    Attributes:
        pool (PostgresPool): The pool the units of work are taken from.
        schema (str): The PostgreSQL schema that holds the outbox.
        logger (Logger): Logger instance.

    Notes:
        - **Nothing here filters by Operator**: row-level security does, so a read made without an Operator returns
          nothing.
        - Each call runs in its own unit of work, so the event commits with it.
    """

    def __init__(self, pool: PostgresPool, schema: str, logger: Optional[Logger] = None) -> None:
        """Prepare a service on a closed pool.

        Args:
            pool (PostgresPool): The pool the units of work are taken from.
            schema (str): The PostgreSQL schema that holds the outbox.
            logger (Optional[Logger]): Logger instance.
        """
        self.pool = pool
        self.schema = schema
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
        self.logger.debug("Event service closed.")

    async def record(self, event: Event) -> Event:
        """Record one event in the outbox, for the Operator of the event.

        Args:
            event (Event): The event.

        Returns:
            Event: The recorded event.

        Raises:
            SEStorageOperatorRefusedError: If the Operator of the event is refused by row-level security.
        """
        async with self.pool.unit_of_work(event.operator_id) as unit_of_work:
            recorded = await OutboxRepository(unit_of_work, self.schema).add(event)
        self.logger.info("Recorded event %s.", recorded.id)
        return recorded

    async def pending(
        self, operator_id: Optional[UUID], limit: int = OutboxRepository.PAGE_SIZE_DEFAULT
    ) -> List[Event]:
        """Read the events not yet published, in recording order.

        Args:
            operator_id (Optional[UUID]): The Operator that reads, or none.
            limit (int): The most events to read.

        Returns:
            List[Event]: The pending events of that Operator, none when there is no Operator.

        Raises:
            SEStorageInvalidPageError: If the limit is outside the bounds.
        """
        async with self.pool.unit_of_work(operator_id) as unit_of_work:
            events = await OutboxRepository(unit_of_work, self.schema).pending(limit)
        self.logger.debug("Read %d pending events.", len(events))
        return events
