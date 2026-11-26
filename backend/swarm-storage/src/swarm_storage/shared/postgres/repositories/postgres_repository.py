from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger, getLogger
from typing import ClassVar, Dict, List, Optional, Union
from uuid import UUID

# Third-party imports
import asyncpg
from pydantic import BaseModel

# First-party imports
from swarm_models.storage.exceptions import (
    SEStorageInvalidPageError,
    SEStorageOperatorRefusedError,
    SEStorageVersionConflictError,
)
from swarm_storage.shared.postgres.ddl.row_level_security import RowLevelSecurity
from swarm_storage.shared.postgres.unit_of_work import UnitOfWork


class PostgresRepository[ModelT: BaseModel](ABC):
    """The base of every PostgreSQL repository: rows to a model and back.

    Attributes:
        TABLE (str): The table of the repository, set by each subclass.
        SCHEMA_KEY (str): The template key of the schema.
        TABLE_KEY (str): The template key of the table.
        ID_KEY (str): The template key of the identifier column.
        VERSION_KEY (str): The template key of the version column.
        ID_COLUMN (str): The primary key column.
        VERSION_COLUMN (str): The column that counts the changes of a row.
        PAGE_SIZE_DEFAULT (int): The page size when none is given.
        PAGE_SIZE_MIN (int): The smallest page size.
        PAGE_SIZE_MAX (int): The largest page size.
        PLACEHOLDER (str): The template of a query parameter.
        ASSIGNMENT (str): The template of a column assignment.
        LIST_SEPARATOR (str): What joins columns, placeholders and assignments.
        INSERT_QUERY (str): The insert template.
        SELECT_QUERY (str): The select-one template.
        PAGE_QUERY (str): The first page template.
        PAGE_AFTER_QUERY (str): The page-after-a-cursor template.
        UPDATE_QUERY (str): The update template, which checks the version.
        DELETE_QUERY (str): The delete template.
        VERSION_QUERY (str): The version template.
        unit_of_work (UnitOfWork): The transaction every query runs in.
        schema (str): The checked schema of the table.
        table (str): The checked table.
        logger (Logger): Logger instance.

    Notes:
        - **No query filters by Operator**: row-level security does, from the setting of the unit of work.
        - A write the policy refuses becomes ``SEStorageOperatorRefusedError``.
        - An update succeeds only if the row still has the expected version, and then increments it. A row of another
          Operator is invisible, so its update reports a conflict.
        - Pages are cursors: rows after an identifier, ordered by identifier.
    """

    TABLE: ClassVar[str]
    SCHEMA_KEY: ClassVar[str] = "schema"
    TABLE_KEY: ClassVar[str] = "table"
    ID_KEY: ClassVar[str] = "id"
    VERSION_KEY: ClassVar[str] = "version"
    ID_COLUMN: ClassVar[str] = "id"
    VERSION_COLUMN: ClassVar[str] = "version"
    PAGE_SIZE_DEFAULT: ClassVar[int] = 100
    PAGE_SIZE_MIN: ClassVar[int] = 1
    PAGE_SIZE_MAX: ClassVar[int] = 500
    PLACEHOLDER: ClassVar[str] = "${position}"
    ASSIGNMENT: ClassVar[str] = "{column} = ${position}"
    LIST_SEPARATOR: ClassVar[str] = ", "
    INSERT_QUERY: ClassVar[str] = "INSERT INTO {schema}.{table} ({columns}) VALUES ({placeholders})"
    SELECT_QUERY: ClassVar[str] = "SELECT * FROM {schema}.{table} WHERE {id} = $1"
    PAGE_QUERY: ClassVar[str] = "SELECT * FROM {schema}.{table} ORDER BY {id} LIMIT $1"
    PAGE_AFTER_QUERY: ClassVar[str] = "SELECT * FROM {schema}.{table} WHERE {id} > $2 ORDER BY {id} LIMIT $1"
    UPDATE_QUERY: ClassVar[str] = (
        "UPDATE {schema}.{table} SET {assignments}, {version} = {version} + 1 "
        "WHERE {id} = $1 AND {version} = $2 RETURNING {version}"
    )
    DELETE_QUERY: ClassVar[str] = "DELETE FROM {schema}.{table} WHERE {id} = $1 RETURNING {id}"
    VERSION_QUERY: ClassVar[str] = "SELECT {version} FROM {schema}.{table} WHERE {id} = $1"

    def __init__(self, unit_of_work: UnitOfWork, schema: str, logger: Optional[Logger] = None) -> None:
        """Prepare a repository on a unit of work.

        Args:
            unit_of_work (UnitOfWork): The transaction every query runs in.
            schema (str): The schema of the table.
            logger (Optional[Logger]): Logger instance.

        Raises:
            SEStorageInvalidIdentifierError: If the schema or the table is not a valid name.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.unit_of_work = unit_of_work
        security = RowLevelSecurity()
        self.schema = security.check(schema)
        self.table = security.check(self.TABLE)

    ############################
    # Internal Helpers Methods #
    ############################

    @abstractmethod
    def to_values(self, model: ModelT) -> Dict[str, Union[str, int, UUID, datetime]]:
        """Map a model to the columns it writes, the identifier first.

        Args:
            model (ModelT): The model.

        Returns:
            Dict[str, Union[str, int, UUID, datetime]]: Column names and values, without the version.
        """

    @abstractmethod
    def to_model(self, record: asyncpg.Record) -> ModelT:
        """Map a row to its model.

        Args:
            record (asyncpg.Record): The row.

        Returns:
            ModelT: The model.
        """

    def names(self) -> Dict[str, str]:
        """Name the table, schema and key columns for a query template.

        Returns:
            Dict[str, str]: The template keys and their checked names.
        """
        return {
            self.SCHEMA_KEY: self.schema,
            self.TABLE_KEY: self.table,
            self.ID_KEY: self.ID_COLUMN,
            self.VERSION_KEY: self.VERSION_COLUMN,
        }

    def check_limit(self, limit: int) -> None:
        """Check a page size.

        Args:
            limit (int): The page size.

        Raises:
            SEStorageInvalidPageError: If it is outside the bounds.
        """
        if not self.PAGE_SIZE_MIN <= limit <= self.PAGE_SIZE_MAX:
            self.logger.error("A page size of %d was refused.", limit)
            raise SEStorageInvalidPageError(
                f"Invalid limit: {limit!r}. Must be an integer in [{self.PAGE_SIZE_MIN}, {self.PAGE_SIZE_MAX}]."
            )
        self.logger.debug("Page size %d accepted.", limit)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def add(self, model: ModelT) -> ModelT:
        """Insert a model.

        Args:
            model (ModelT): The model to store.

        Returns:
            ModelT: The same model.

        Raises:
            SEStorageOperatorRefusedError: If the policy refuses the row, such as another Operator's.
        """
        values = self.to_values(model)
        security = RowLevelSecurity()
        columns = [security.check(column) for column in values]
        placeholders = [self.PLACEHOLDER.format(position=position) for position in range(1, len(columns) + 1)]
        query = self.INSERT_QUERY.format(
            **self.names(),
            columns=self.LIST_SEPARATOR.join(columns),
            placeholders=self.LIST_SEPARATOR.join(placeholders),
        )
        try:
            await self.unit_of_work.connection.execute(query, *values.values())
        except asyncpg.exceptions.InsufficientPrivilegeError as error:
            self.logger.error("The insert was refused by row-level security.")
            raise SEStorageOperatorRefusedError("The row is refused: it does not belong to the Operator.") from error
        self.logger.debug("Row added to %s.", self.table)
        return model

    async def get(self, identifier: UUID) -> Optional[ModelT]:
        """Read one model.

        Args:
            identifier (UUID): Its identifier.

        Returns:
            Optional[ModelT]: The model, or none if the Operator has no such row.
        """
        record = await self.unit_of_work.connection.fetchrow(self.SELECT_QUERY.format(**self.names()), identifier)
        if record is None:
            self.logger.debug("No row %s in %s for this Operator.", identifier, self.table)
            return None
        return self.to_model(record)

    async def list(self, after: Optional[UUID] = None, limit: int = PAGE_SIZE_DEFAULT) -> List[ModelT]:
        """Read a page of models, ordered by identifier.

        Args:
            after (Optional[UUID]): The cursor: only identifiers greater than this one, or none for the first page.
            limit (int): The page size.

        Returns:
            List[ModelT]: The models of the page.

        Raises:
            SEStorageInvalidPageError: If the limit is outside the bounds.
        """
        self.check_limit(limit)
        connection = self.unit_of_work.connection
        if after is None:
            records = await connection.fetch(self.PAGE_QUERY.format(**self.names()), limit)
        else:
            records = await connection.fetch(self.PAGE_AFTER_QUERY.format(**self.names()), limit, after)
        return [self.to_model(record) for record in records]

    async def version_of(self, identifier: UUID) -> Optional[int]:
        """Read the version of a row.

        Args:
            identifier (UUID): Its identifier.

        Returns:
            Optional[int]: The version, or none if the Operator has no such row.
        """
        value = await self.unit_of_work.connection.fetchval(self.VERSION_QUERY.format(**self.names()), identifier)
        if value is None:
            self.logger.debug("No row %s in %s for this Operator.", identifier, self.table)
            return None
        return int(value)

    async def update(self, model: ModelT, expected_version: int) -> int:
        """Change a row if it still has the expected version.

        Args:
            model (ModelT): The new state.
            expected_version (int): The version the caller read.

        Returns:
            int: The new version.

        Raises:
            SEStorageVersionConflictError: If the row changed, or is not visible to the Operator.
            SEStorageOperatorRefusedError: If the policy refuses the new row.
        """
        values = self.to_values(model)
        security = RowLevelSecurity()
        identifier = values.pop(self.ID_COLUMN)
        assignments = [
            self.ASSIGNMENT.format(column=security.check(column), position=position)
            for position, column in enumerate(values, start=3)
        ]
        query = self.UPDATE_QUERY.format(**self.names(), assignments=self.LIST_SEPARATOR.join(assignments))
        try:
            version = await self.unit_of_work.connection.fetchval(query, identifier, expected_version, *values.values())
        except asyncpg.exceptions.InsufficientPrivilegeError as error:
            self.logger.error("The update was refused by row-level security.")
            raise SEStorageOperatorRefusedError("The row is refused: it does not belong to the Operator.") from error
        if version is None:
            self.logger.error("The update of %s found no row at version %d.", identifier, expected_version)
            raise SEStorageVersionConflictError(
                f"Version conflict on {identifier}. No row has version {expected_version}."
            )
        self.logger.debug("Row %s of %s is now at version %d.", identifier, self.table, version)
        return int(version)

    async def delete(self, identifier: UUID) -> bool:
        """Delete a row.

        Args:
            identifier (UUID): Its identifier.

        Returns:
            bool: True if a row was deleted, false if the Operator has no such row.
        """
        deleted = await self.unit_of_work.connection.fetchval(self.DELETE_QUERY.format(**self.names()), identifier)
        if deleted is None:
            self.logger.debug("No row %s to delete in %s.", identifier, self.table)
            return False
        self.logger.debug("Row %s deleted from %s.", identifier, self.table)
        return True
