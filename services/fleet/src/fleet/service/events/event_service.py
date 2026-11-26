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
    """The events of the fleet service, recorded in its outbox and read back.

    Attributes:
        pool (PostgresPool): The pool the units of work come from.
        schema (str): The schema of the outbox.
        logger (Logger): Logger instance.

    Notes:
        - **``pending`` never filters by Operator**: row-level security does, so a call with no Operator or an
          unknown one returns nothing.
    """

    def __init__(self, pool: PostgresPool, schema: str, logger: Optional[Logger] = None) -> None:
        """Prepare the service, closed.

        Args:
            pool (PostgresPool): The pool the units of work come from.
            schema (str): The schema of the outbox.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.pool = pool
        self.schema = schema

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
        self.logger.debug("The event service is open.")

    async def close(self) -> None:
        """Close the pool, safely before ``open`` and when called twice."""
        await self.pool.close()
        self.logger.debug("The event service is closed.")

    async def record(self, event: Event) -> Event:
        """Record an event in the outbox, in the transaction of its Operator.

        Args:
            event (Event): The event to record.

        Returns:
            Event: The recorded event.

        Raises:
            SEStorageNotOpenError: If the service is not open.
            SEStorageOperatorRefusedError: If the row is refused by row-level security.
        """
        async with self.pool.unit_of_work(event.operator_id) as unit_of_work:
            recorded = await OutboxRepository(unit_of_work, self.schema).add(event)
        self.logger.info("Recorded event %s.", recorded.id)
        return recorded

    async def pending(self, operator_id: Optional[UUID]) -> List[Event]:
        """Read the events not yet published, in recording order.

        Args:
            operator_id (Optional[UUID]): The Operator the work is done for, or none.

        Returns:
            List[Event]: The pending events of that Operator, none for no Operator or an unknown one.

        Raises:
            SEStorageNotOpenError: If the service is not open.
        """
        async with self.pool.unit_of_work(operator_id) as unit_of_work:
            events = await OutboxRepository(unit_of_work, self.schema).pending()
        self.logger.debug("Read %d pending events.", len(events))
        return events
