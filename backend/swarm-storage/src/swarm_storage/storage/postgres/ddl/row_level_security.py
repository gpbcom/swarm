from __future__ import annotations

# Standard library imports
import re
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional, Pattern

# First-party imports
from swarm_storage.models.postgres.exceptions import SEStorageInvalidIdentifierError
from swarm_storage.storage.postgres.unit_of_work import UnitOfWork


class RowLevelSecurity:
    """The statements that isolate the rows of a table by Operator.

    Attributes:
        POLICY_NAME (str): The name of the policy created on each table.
        OPERATOR_COLUMN (str): The column that holds the owning Operator.
        SCHEMA_KEY (str): The template key of the schema.
        TABLE_KEY (str): The template key of the table.
        IDENTIFIER_PATTERN (Pattern[str]): The shape of an accepted schema, table or column name.
        ENABLE_STATEMENT (str): The statement that enables row-level security.
        FORCE_STATEMENT (str): The statement that applies it to the table owner too.
        POLICY_STATEMENT (str): The statement that creates the policy.
        DISABLE_POLICY_STATEMENT (str): The statement that drops the policy.
        DISABLE_STATEMENT (str): The statement that disables row-level security.
        NO_FORCE_STATEMENT (str): The statement that stops forcing it on the owner.
        logger (Logger): Logger instance.

    Notes:
        - **An unset setting matches no row**, because the policy compares ``operator_id`` with a ``NULLIF`` of it.
        - Names are checked against ``IDENTIFIER_PATTERN`` and then written as they are, so no value can carry SQL.
    """

    POLICY_NAME: ClassVar[str] = "operator_isolation"
    OPERATOR_COLUMN: ClassVar[str] = "operator_id"
    SCHEMA_KEY: ClassVar[str] = "schema"
    TABLE_KEY: ClassVar[str] = "table"
    IDENTIFIER_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[a-z_][a-z0-9_]*$")
    ENABLE_STATEMENT: ClassVar[str] = "ALTER TABLE {schema}.{table} ENABLE ROW LEVEL SECURITY"
    FORCE_STATEMENT: ClassVar[str] = "ALTER TABLE {schema}.{table} FORCE ROW LEVEL SECURITY"
    POLICY_STATEMENT: ClassVar[str] = (
        "CREATE POLICY {policy} ON {schema}.{table} "
        "USING ({column} = NULLIF(current_setting('{setting}', true), '')::uuid) "
        "WITH CHECK ({column} = NULLIF(current_setting('{setting}', true), '')::uuid)"
    )
    DISABLE_POLICY_STATEMENT: ClassVar[str] = "DROP POLICY IF EXISTS {policy} ON {schema}.{table}"
    DISABLE_STATEMENT: ClassVar[str] = "ALTER TABLE {schema}.{table} DISABLE ROW LEVEL SECURITY"
    NO_FORCE_STATEMENT: ClassVar[str] = "ALTER TABLE {schema}.{table} NO FORCE ROW LEVEL SECURITY"

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Prepare the statement builder.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def checked_names(self, schema: str, table: str) -> Dict[str, str]:
        """Check the schema and the table, and name them for a template.

        Args:
            schema (str): The schema.
            table (str): The table.

        Returns:
            Dict[str, str]: The checked names, keyed by ``SCHEMA_KEY`` and ``TABLE_KEY``.

        Raises:
            SEStorageInvalidIdentifierError: If a name is not valid.
        """
        return {self.SCHEMA_KEY: self.check(schema), self.TABLE_KEY: self.check(table)}

    ############################
    # Publicly Exposed Methods #
    ############################

    def check(self, name: str) -> str:
        """Check a schema, table or column name.

        Args:
            name (str): The name to check.

        Returns:
            str: The same name.

        Raises:
            SEStorageInvalidIdentifierError: If the name is not lower case letters, digits and underscores.
        """
        if not self.IDENTIFIER_PATTERN.match(name):
            self.logger.error("An invalid identifier was refused.")
            raise SEStorageInvalidIdentifierError(
                f"Invalid identifier: {name!r}. Must match {self.IDENTIFIER_PATTERN.pattern}."
            )
        self.logger.debug("Identifier %s accepted.", name)
        return name

    def enable(self, schema: str, table: str) -> List[str]:
        """Build the statements that isolate a table by Operator.

        Args:
            schema (str): The schema of the table.
            table (str): The table, which must have an ``operator_id`` column.

        Returns:
            List[str]: ENABLE, FORCE, then the policy.

        Raises:
            SEStorageInvalidIdentifierError: If a name is not valid.
        """
        names = self.checked_names(schema, table)
        self.logger.debug("Row-level security statements built for %s.%s.", schema, table)
        return [
            self.ENABLE_STATEMENT.format(**names),
            self.FORCE_STATEMENT.format(**names),
            self.POLICY_STATEMENT.format(
                policy=self.POLICY_NAME, column=self.OPERATOR_COLUMN, setting=UnitOfWork.OPERATOR_SETTING, **names
            ),
        ]

    def disable(self, schema: str, table: str) -> List[str]:
        """Build the statements that undo ``enable``.

        Args:
            schema (str): The schema of the table.
            table (str): The table.

        Returns:
            List[str]: Drop the policy, stop forcing, disable.

        Raises:
            SEStorageInvalidIdentifierError: If a name is not valid.
        """
        names = self.checked_names(schema, table)
        self.logger.debug("Row-level security removal statements built for %s.%s.", schema, table)
        return [
            self.DISABLE_POLICY_STATEMENT.format(policy=self.POLICY_NAME, **names),
            self.NO_FORCE_STATEMENT.format(**names),
            self.DISABLE_STATEMENT.format(**names),
        ]
