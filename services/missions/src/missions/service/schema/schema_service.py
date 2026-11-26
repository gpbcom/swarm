from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# First-party imports
from swarm_storage.shared.postgres.migrations.alembic_migrator import AlembicMigrator


class SchemaService:
    """Brings the PostgreSQL schema of missions to a revision, and tells which one it is at.

    Attributes:
        BASE (str): The revision that means no migration applied.
        migrator (AlembicMigrator): The migrator of the service, bound to its schema and migration folder.
        logger (Logger): Logger instance.

    Notes:
        **The DSN is read from the environment by the migrator and is never logged.**
    """

    BASE: ClassVar[str] = "base"

    def __init__(self, migrator: AlembicMigrator, logger: Optional[Logger] = None) -> None:
        """Prepare a service.

        Args:
            migrator (AlembicMigrator): The migrator of the service.
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
        self.logger.info("Missions schema upgraded.")

    async def downgrade_to_base(self) -> None:
        """Undo every migration.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the migration fails.
        """
        await self.migrator.downgrade(self.BASE)
        self.logger.info("Missions schema downgraded to base.")

    async def current(self) -> Optional[str]:
        """Read the applied revision.

        Returns:
            Optional[str]: The revision, or none if nothing is applied.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the database cannot be read.
        """
        revision = await self.migrator.current()
        self.logger.debug("Missions schema is at %s.", revision)
        return revision
