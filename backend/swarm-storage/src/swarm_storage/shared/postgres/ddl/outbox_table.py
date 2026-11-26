from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, List, Optional

# First-party imports
from swarm_storage.shared.postgres.ddl.row_level_security import RowLevelSecurity


class OutboxTable:
    """The statements that create and drop the outbox table of a service schema.

    Attributes:
        TABLE (str): The name of the table.
        CREATE_STATEMENT (str): The statement that creates the table.
        INDEX_STATEMENT (str): The statement that indexes it by Operator and identifier.
        DROP_STATEMENT (str): The statement that drops it.
        logger (Logger): Logger instance.

    Notes:
        - The table is written in the same transaction as the business change, and a relay publishes it afterwards.
        - **Row-level security is enabled by the creation statements**, like on every Operator-owned table.
    """

    TABLE: ClassVar[str] = "outbox"
    CREATE_STATEMENT: ClassVar[str] = (
        "CREATE TABLE {schema}.{table} ("
        "id uuid PRIMARY KEY, "
        "operator_id uuid NOT NULL, "
        "version integer NOT NULL DEFAULT 1, "
        "event jsonb NOT NULL, "
        "recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(), "
        "published_at timestamptz)"
    )
    INDEX_STATEMENT: ClassVar[str] = "CREATE INDEX {table}_operator_id_id_idx ON {schema}.{table} (operator_id, id)"
    DROP_STATEMENT: ClassVar[str] = "DROP TABLE IF EXISTS {schema}.{table}"

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Prepare the statement builder.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.security = RowLevelSecurity()

    ############################
    # Publicly Exposed Methods #
    ############################

    def create(self, schema: str) -> List[str]:
        """Build the statements that create the outbox.

        Args:
            schema (str): The schema of the service.

        Returns:
            List[str]: The table, its index, then the row-level security statements.

        Raises:
            SEStorageInvalidIdentifierError: If the schema is not valid.
        """
        names = self.security.checked_names(schema, self.TABLE)
        self.logger.debug("Outbox creation statements built for %s.", schema)
        return [
            self.CREATE_STATEMENT.format(**names),
            self.INDEX_STATEMENT.format(**names),
            *self.security.enable(schema, self.TABLE),
        ]

    def drop(self, schema: str) -> List[str]:
        """Build the statements that drop the outbox.

        Args:
            schema (str): The schema of the service.

        Returns:
            List[str]: The drop statement.

        Raises:
            SEStorageInvalidIdentifierError: If the schema is not valid.
        """
        names = self.security.checked_names(schema, self.TABLE)
        self.logger.debug("Outbox drop statements built for %s.", schema)
        return [self.DROP_STATEMENT.format(**names)]
