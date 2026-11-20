from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import ClassVar, Dict, List, Union
from uuid import UUID

# Third-party imports
import asyncpg

# First-party imports
from swarm_models.models.events.event import Event
from swarm_storage.storage.postgres.ddl.outbox_table import OutboxTable
from swarm_storage.storage.postgres.repositories.postgres_repository import PostgresRepository


class OutboxRepository(PostgresRepository[Event]):
    """The events waiting to be published, stored in the transaction of the change that made them.

    Attributes:
        TABLE (str): The outbox table.
        OPERATOR_COLUMN (str): The column of the owning Operator.
        EVENT_COLUMN (str): The column that holds the event as JSON.
        PENDING_QUERY (str): The query for the events not yet published.
        PUBLISHED_QUERY (str): The statement that marks an event published.

    Notes:
        - **Nothing here filters by Operator**: row-level security does.
        - The ``version`` column belongs to the row, and ``Event.version`` to the type, so they are unrelated.
    """

    TABLE: ClassVar[str] = OutboxTable.TABLE
    OPERATOR_COLUMN: ClassVar[str] = "operator_id"
    EVENT_COLUMN: ClassVar[str] = "event"
    PENDING_QUERY: ClassVar[str] = (
        "SELECT * FROM {schema}.{table} WHERE published_at IS NULL ORDER BY recorded_at, {id} LIMIT $1"
    )
    PUBLISHED_QUERY: ClassVar[str] = (
        "UPDATE {schema}.{table} SET published_at = clock_timestamp() "
        "WHERE {id} = $1 AND published_at IS NULL RETURNING {id}"
    )

    ############################
    # Internal Helpers Methods #
    ############################

    def to_values(self, model: Event) -> Dict[str, Union[str, int, UUID, datetime]]:
        """Map an event to the columns it writes.

        Args:
            model (Event): The event.

        Returns:
            Dict[str, Union[str, int, UUID, datetime]]: The identifier, the Operator and the JSON of the event.
        """
        return {
            self.ID_COLUMN: model.id,
            self.OPERATOR_COLUMN: model.operator_id,
            self.EVENT_COLUMN: model.model_dump_json(),
        }

    def to_model(self, record: asyncpg.Record) -> Event:
        """Map a row to its event.

        Args:
            record (asyncpg.Record): The row.

        Returns:
            Event: The event.
        """
        return Event.model_validate_json(record[self.EVENT_COLUMN])

    ############################
    # Publicly Exposed Methods #
    ############################

    async def pending(self, limit: int = PostgresRepository.PAGE_SIZE_DEFAULT) -> List[Event]:
        """Read the events not yet published, in recording order.

        Args:
            limit (int): The most events to read.

        Returns:
            List[Event]: The pending events of the Operator.

        Raises:
            SEStorageInvalidPageError: If the limit is outside the bounds.
        """
        self.check_limit(limit)
        records = await self.unit_of_work.connection.fetch(self.PENDING_QUERY.format(**self.names()), limit)
        return [self.to_model(record) for record in records]

    async def mark_published(self, identifier: UUID) -> bool:
        """Mark an event as published.

        Args:
            identifier (UUID): The identifier of the event.

        Returns:
            bool: True if it was pending, false if it is unknown, already published or another Operator's.
        """
        marked = await self.unit_of_work.connection.fetchval(self.PUBLISHED_QUERY.format(**self.names()), identifier)
        if marked is None:
            self.logger.debug("Event %s was not pending for this Operator.", identifier)
            return False
        self.logger.debug("Event %s marked published.", identifier)
        return True
