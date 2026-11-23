from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# First-party imports
from swarm_storage.storage.postgres.migrations.alembic_migrator import AlembicMigrator


class SchemaService:
    """The schema of the fleet service: upgrading it, downgrading it and reading its revision.

    Attributes:
        BASE (str): The revision that means no migration applied.
        migrator (AlembicMigrator): The migrator of the fleet schema.
        logger (Logger): Logger instance.

    Notes:
        - Callers go through this class so that the schema rules stay in one place, and the migrator stays a detail.
    """

    BASE: ClassVar[str] = "base"

    def __init__(self, migrator: AlembicMigrator, logger: Optional[Logger] = None) -> None:
        """Prepare the service.

        Args:
            migrator (AlembicMigrator): The migrator of the fleet schema.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.migrator = migrator

    ############################
    # Publicly Exposed Methods #
    ############################

    async def upgrade(self) -> None:
        """Apply every migration, creating the schema if it is missing.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the migration fails.
        """
        self.logger.debug("Upgrading the schema to the latest revision.")
        await self.migrator.upgrade()
        self.logger.info("The schema is at the latest revision.")

    async def downgrade_to_base(self) -> None:
        """Undo every migration.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the migration fails.
        """
        self.logger.debug("Downgrading the schema to its base.")
        await self.migrator.downgrade(self.BASE)
        self.logger.info("The schema is at its base.")

    async def current(self) -> Optional[str]:
        """Read the applied revision.

        Returns:
            Optional[str]: The revision, or none if nothing is applied.

        Raises:
            SEStorageDsnMissingError: If the environment entry of the DSN is not set.
            SEStorageMigrationError: If the database cannot be read.
        """
        revision = await self.migrator.current()
        if revision is None:
            self.logger.debug("No revision is applied.")
        else:
            self.logger.debug("The applied revision is %s.", revision)
        return revision
