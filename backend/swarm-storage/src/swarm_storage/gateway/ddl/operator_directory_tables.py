from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, List, Optional

# First-party imports
from swarm_storage.shared.postgres.ddl.row_level_security import RowLevelSecurity


class OperatorDirectoryTables:
    """The statements that create and drop the Operator directory tables of the gateway schema.

    Attributes:
        OPERATORS_TABLE (str): The table of the Operators.
        CELL_ASSIGNMENTS_TABLE (str): The table that maps each Operator to its cell.
        PEOPLE_TABLE (str): The table of the people.
        OPERATORS_STATEMENT (str): The statement that creates the Operators table.
        NAME_INDEX_STATEMENT (str): The statement that makes an Operator name unique, without case and spaces.
        CELL_ASSIGNMENTS_STATEMENT (str): The statement that creates the cell assignments table.
        PEOPLE_STATEMENT (str): The statement that creates the people table.
        PEOPLE_INDEX_STATEMENT (str): The statement that indexes the people by Operator and identifier.
        DROP_STATEMENT (str): The statement that drops a table.
        logger (Logger): Logger instance.

    Notes:
        - **The ``operators`` and ``cell_assignments`` tables have no row-level security**: they are global, and the
          Swarm administrator writes them without an Operator, so a policy on the Operator setting would hide every row.
        - The ``people`` table belongs to an Operator, so it has row-level security.
        - The unique index on ``lower(btrim(name))`` makes two Operators with the same name, ignoring case and
          surrounding spaces, impossible.
    """

    OPERATORS_TABLE: ClassVar[str] = "operators"
    CELL_ASSIGNMENTS_TABLE: ClassVar[str] = "cell_assignments"
    PEOPLE_TABLE: ClassVar[str] = "people"
    OPERATORS_STATEMENT: ClassVar[str] = (
        "CREATE TABLE {schema}.{table} ("
        "id uuid PRIMARY KEY, "
        "version integer NOT NULL DEFAULT 1, "
        "name text NOT NULL, "
        "deployment text NOT NULL, "
        "jurisdictions text[] NOT NULL, "
        "llm_provider text NOT NULL, "
        "anchoring text NOT NULL)"
    )
    NAME_INDEX_STATEMENT: ClassVar[str] = (
        "CREATE UNIQUE INDEX {table}_name_unique_idx ON {schema}.{table} (lower(btrim(name)))"
    )
    CELL_ASSIGNMENTS_STATEMENT: ClassVar[str] = (
        "CREATE TABLE {schema}.{table} ("
        "operator_id uuid PRIMARY KEY, "
        "version integer NOT NULL DEFAULT 1, "
        "cell text NOT NULL, "
        "assigned_at timestamptz NOT NULL)"
    )
    PEOPLE_STATEMENT: ClassVar[str] = (
        "CREATE TABLE {schema}.{table} ("
        "id uuid PRIMARY KEY, "
        "operator_id uuid, "
        "version integer NOT NULL DEFAULT 1, "
        "name text NOT NULL, "
        "email text NOT NULL, "
        "language text NOT NULL)"
    )
    PEOPLE_INDEX_STATEMENT: ClassVar[str] = (
        "CREATE INDEX {table}_operator_id_id_idx ON {schema}.{table} (operator_id, id)"
    )
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
        """Build the statements that create the three tables.

        Args:
            schema (str): The schema of the gateway.

        Returns:
            List[str]: The tables and indexes, then the row-level security statements of the people table.

        Raises:
            SEStorageInvalidIdentifierError: If the schema is not valid.
        """
        operators = self.security.checked_names(schema, self.OPERATORS_TABLE)
        assignments = self.security.checked_names(schema, self.CELL_ASSIGNMENTS_TABLE)
        people = self.security.checked_names(schema, self.PEOPLE_TABLE)
        self.logger.debug("Operator directory creation statements built for %s.", schema)
        return [
            self.OPERATORS_STATEMENT.format(**operators),
            self.NAME_INDEX_STATEMENT.format(**operators),
            self.CELL_ASSIGNMENTS_STATEMENT.format(**assignments),
            self.PEOPLE_STATEMENT.format(**people),
            self.PEOPLE_INDEX_STATEMENT.format(**people),
            *self.security.enable(schema, self.PEOPLE_TABLE),
        ]

    def drop(self, schema: str) -> List[str]:
        """Build the statements that drop the three tables.

        Args:
            schema (str): The schema of the gateway.

        Returns:
            List[str]: One drop statement per table.

        Raises:
            SEStorageInvalidIdentifierError: If the schema is not valid.
        """
        tables = [self.PEOPLE_TABLE, self.CELL_ASSIGNMENTS_TABLE, self.OPERATORS_TABLE]
        statements = [self.DROP_STATEMENT.format(**self.security.checked_names(schema, table)) for table in tables]
        self.logger.debug("Operator directory drop statements built for %s.", schema)
        return statements
