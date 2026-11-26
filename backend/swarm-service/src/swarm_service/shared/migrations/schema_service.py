from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# First-party imports
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator


class SchemaService:
    """Moves the PostgreSQL schema of an app between revisions.

    Attributes:
        BASE (str): The revision that means no migration applied.
        migrator (AlembicMigrator): The migrator of the app's schema.
        logger (Logger): Logger instance.

    Notes:
        - Migrations go expand then contract.
    """

    BASE: ClassVar[str] = "base"

    def __init__(self, migrator: AlembicMigrator, logger: Optional[Logger] = None) -> None:
        """Prepare the service.

        Args:
            migrator (AlembicMigrator): The migrator of the app's schema.
            logger (Optional[Logger]): Logger instance.
        """
        self.migrator = migrator
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def upgrade(self) -> None:
        """Apply every migration, creating the schema if it is missing.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the migration fails.
        """
        await self.migrator.upgrade()
        self.logger.info("Schema upgraded to the latest revision.")

    async def downgrade_to_base(self) -> None:
        """Undo every migration.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the migration fails.
        """
        await self.migrator.downgrade(self.BASE)
        self.logger.info("Schema downgraded to base.")

    async def current(self) -> Optional[str]:
        """Read the applied revision.

        Returns:
            Optional[str]: The revision, or none if nothing is applied.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the database cannot be read.
        """
        revision = await self.migrator.current()
        self.logger.debug("The schema is at %s.", revision)
        return revision
