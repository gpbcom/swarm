from __future__ import annotations

# Standard library imports
import os
from logging import Logger, getLogger
from pathlib import Path
from typing import Callable, ClassVar, Optional

# Third-party imports
import asyncpg
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.util.exc import CommandError
from sqlalchemy import Connection, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# First-party imports
from swarm_storage.models.config.postgres_config import PostgresConfig
from swarm_storage.models.postgres.exceptions import SEStorageDsnMissingError, SEStorageMigrationError
from swarm_storage.storage.postgres.ddl.row_level_security import RowLevelSecurity


class AlembicMigrator:
    """Runs the Alembic migrations of one service, in that service's schema.

    Attributes:
        SCHEMA_ATTRIBUTE (str): The ``Config.attributes`` key that carries the schema to each ``env.py``.
        CONNECTION_ATTRIBUTE (str): The ``Config.attributes`` key that carries the open connection.
        SCRIPT_LOCATION_OPTION (str): The Alembic option that names the migration folder.
        ASYNC_DRIVER (str): The SQLAlchemy driver name used with the DSN.
        HEAD (str): The revision that means the latest one.
        PERCENT (str): The character that a configuration value must double.
        ESCAPED_PERCENT (str): Its doubled form.
        CREATE_SCHEMA_STATEMENT (str): The statement that creates the schema if it is missing.
        VERSION_TABLE_SCHEMA_OPTION (str): The ``MigrationContext`` option that places ``alembic_version``.
        config (PostgresConfig): The connection settings, which name the environment entry of the DSN.
        schema (str): The schema of the service.
        script_location (Path): The folder of the migrations, with its ``env.py``.
        logger (Logger): Logger instance.

    Notes:
        - **The DSN is read from the environment and never logged.**
        - Migrations go expand then contract: a release only adds, and a later one removes what nothing reads.
        - ``alembic_version`` lives in the service's schema, so each service has its own history.
    """

    SCHEMA_ATTRIBUTE: ClassVar[str] = "swarm_schema"
    CONNECTION_ATTRIBUTE: ClassVar[str] = "swarm_connection"
    SCRIPT_LOCATION_OPTION: ClassVar[str] = "script_location"
    ASYNC_DRIVER: ClassVar[str] = "postgresql+asyncpg"
    HEAD: ClassVar[str] = "head"
    PERCENT: ClassVar[str] = "%"
    ESCAPED_PERCENT: ClassVar[str] = "%%"
    CREATE_SCHEMA_STATEMENT: ClassVar[str] = "CREATE SCHEMA IF NOT EXISTS {schema}"
    VERSION_TABLE_SCHEMA_OPTION: ClassVar[str] = "version_table_schema"

    def __init__(
        self, config: PostgresConfig, schema: str, script_location: Path, logger: Optional[Logger] = None
    ) -> None:
        """Prepare a migrator.

        Args:
            config (PostgresConfig): The connection settings.
            schema (str): The schema of the service.
            script_location (Path): The folder of the migrations.
            logger (Optional[Logger]): Logger instance.

        Raises:
            SEStorageInvalidIdentifierError: If the schema is not a valid name.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.schema = RowLevelSecurity().check(schema)
        self.script_location = script_location

    ############################
    # Internal Helpers Methods #
    ############################

    def build_config(self, connection: Connection) -> Config:
        """Build the Alembic configuration for one connection.

        Args:
            connection (Connection): The synchronous view of the open connection.

        Returns:
            Config: The configuration, with the schema and the connection in its attributes.
        """
        alembic_config = Config()
        location = str(self.script_location).replace(self.PERCENT, self.ESCAPED_PERCENT)
        alembic_config.set_main_option(self.SCRIPT_LOCATION_OPTION, location)
        alembic_config.attributes[self.SCHEMA_ATTRIBUTE] = self.schema
        alembic_config.attributes[self.CONNECTION_ATTRIBUTE] = connection
        return alembic_config

    def upgrade_sync(self, connection: Connection, revision: str) -> Optional[str]:
        """Upgrade, inside the synchronous view of the connection.

        Args:
            connection (Connection): The connection.
            revision (str): The target revision.

        Returns:
            Optional[str]: None.
        """
        command.upgrade(self.build_config(connection), revision)
        return None

    def downgrade_sync(self, connection: Connection, revision: str) -> Optional[str]:
        """Downgrade, inside the synchronous view of the connection.

        Args:
            connection (Connection): The connection.
            revision (str): The target revision.

        Returns:
            Optional[str]: None.
        """
        command.downgrade(self.build_config(connection), revision)
        return None

    def current_sync(self, connection: Connection, revision: str) -> Optional[str]:
        """Read the applied revision, inside the synchronous view of the connection.

        Args:
            connection (Connection): The connection.
            revision (str): Unused, so that the three work functions share one signature.

        Returns:
            Optional[str]: The applied revision, or none.
        """
        context = MigrationContext.configure(connection, opts={self.VERSION_TABLE_SCHEMA_OPTION: self.schema})
        return context.get_current_revision()

    async def run_work(
        self, work: Callable[[Connection, str], Optional[str]], revision: str, create_schema: bool
    ) -> Optional[str]:
        """Run one piece of work on a fresh connection, in one transaction.

        Args:
            work (Callable[[Connection, str], Optional[str]]): The work, given the connection and the revision.
            revision (str): The revision it works on.
            create_schema (bool): Whether to create the schema first.

        Returns:
            Optional[str]: What the work returns.

        Raises:
            SEStorageDsnMissingError: If the environment entry is not set.
            SEStorageMigrationError: If the folder is missing or the migration fails.
        """
        if not self.script_location.is_dir():
            self.logger.error("The migration folder does not exist.")
            raise SEStorageMigrationError(f"The migration folder does not exist: {self.script_location}.")
        dsn = os.environ.get(self.config.dsn_key)
        if not dsn:
            self.logger.error("The environment entry %s is not set.", self.config.dsn_key)
            raise SEStorageDsnMissingError(f"The environment entry {self.config.dsn_key} is not set.")
        engine = create_async_engine(make_url(dsn).set(drivername=self.ASYNC_DRIVER), poolclass=NullPool)
        try:
            async with engine.begin() as connection:
                if create_schema:
                    await connection.execute(text(self.CREATE_SCHEMA_STATEMENT.format(schema=self.schema)))
                else:
                    self.logger.debug("The schema is not created for this work.")
                return await connection.run_sync(work, revision)
        except (CommandError, SQLAlchemyError, asyncpg.PostgresError, OSError) as error:
            self.logger.error("The migration failed: %s.", type(error).__name__)
            raise SEStorageMigrationError(f"The migration failed: {type(error).__name__}.") from error
        finally:
            await engine.dispose()

    ############################
    # Publicly Exposed Methods #
    ############################

    async def upgrade(self, revision: str = HEAD) -> None:
        """Apply the migrations up to a revision, creating the schema if it is missing.

        Args:
            revision (str): The target revision, the latest by default.

        Raises:
            SEStorageDsnMissingError: If the environment entry is not set.
            SEStorageMigrationError: If the migration fails.
        """
        await self.run_work(self.upgrade_sync, revision, True)
        self.logger.info("Schema %s upgraded to %s.", self.schema, revision)

    async def downgrade(self, revision: str) -> None:
        """Undo the migrations down to a revision.

        Args:
            revision (str): The target revision, ``base`` for none.

        Raises:
            SEStorageDsnMissingError: If the environment entry is not set.
            SEStorageMigrationError: If the migration fails.
        """
        await self.run_work(self.downgrade_sync, revision, False)
        self.logger.info("Schema %s downgraded to %s.", self.schema, revision)

    async def current(self) -> Optional[str]:
        """Read the applied revision.

        Returns:
            Optional[str]: The revision, or none if nothing is applied.

        Raises:
            SEStorageDsnMissingError: If the environment entry is not set.
            SEStorageMigrationError: If the database cannot be read.
        """
        revision = await self.run_work(self.current_sync, self.HEAD, False)
        self.logger.debug("Schema %s is at %s.", self.schema, revision)
        return revision
