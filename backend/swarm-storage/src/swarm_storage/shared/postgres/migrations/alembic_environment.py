from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# Third-party imports
from alembic import context
from sqlalchemy import Connection

# First-party imports
from swarm_lifecycle.runnables.runnable import Runnable
from swarm_models.storage.exceptions import SEStorageMigrationError
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator


class AlembicEnvironment(Runnable):
    """What every ``env.py`` of a service runs: the migrations on the connection of the migrator.

    Attributes:
        logger (Logger): Logger instance.

    Notes:
        - It works in online mode only: **offline mode raises ``SEStorageMigrationError``**, because the schema
          comes from the migrator.
        - ``alembic_version`` is kept in the schema the migrator passed.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Prepare the environment.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(logger if logger else getLogger(__name__))

    ############################
    # Publicly Exposed Methods #
    ############################

    def initialize(self) -> None:
        """Acquire nothing: the migrator owns the connection."""
        self.logger.debug("The migrator owns the connection: nothing to acquire.")

    def close(self) -> None:
        """Release nothing: the migrator closes the connection."""
        self.logger.debug("The migrator closes the connection: nothing to release.")

    def run(self) -> None:
        """Run the migrations of the current Alembic context.

        Raises:
            SEStorageMigrationError: If Alembic is in offline mode or no connection was passed.
        """
        if context.is_offline_mode():
            self.logger.error("Offline mode is not supported.")
            raise SEStorageMigrationError("Offline mode is not supported. Run the migrations online.")
        attributes = context.config.attributes
        connection: Optional[Connection] = attributes.get(AlembicMigrator.CONNECTION_ATTRIBUTE)
        schema: Optional[str] = attributes.get(AlembicMigrator.SCHEMA_ATTRIBUTE)
        if connection is None or schema is None:
            self.logger.error("The migrator passed no connection or no schema.")
            raise SEStorageMigrationError("The migrator passed no connection or no schema.")
        context.configure(connection=connection, version_table_schema=schema)
        with context.begin_transaction():
            context.run_migrations()
        self.logger.info("Migrations ran in schema %s.", schema)
