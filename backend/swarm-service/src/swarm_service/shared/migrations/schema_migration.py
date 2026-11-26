from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import AsyncIterator, Optional

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.storage.exceptions import SEStorageError
from swarm_service.shared.migrations.schema_service import SchemaService


class SchemaMigration(AsyncRunnable):
    """The migration that upgrades the PostgreSQL schema of an app to its latest revision.

    Attributes:
        service (SchemaService): The service that applies the migrations.
        exit_code (int): ``0`` unless a storage error stopped the migration, then ``1``.
        logger (Logger): Logger instance.

    Notes:
        - **A storage error never escapes ``execute``**: it is logged, gives ``exit_code`` 1 and ends the statuses
          without ``EXECUTED``, so that the migration job fails by its exit code.
    """

    def __init__(self, service: SchemaService, status_interval_s: float, logger: Optional[Logger] = None) -> None:
        """Prepare the migration.

        Args:
            service (SchemaService): The service that applies the migrations.
            status_interval_s (float): Seconds between two statuses, from the configuration.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.service = service
        self.exit_code = 0

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Acquire nothing: the service opens its own connection."""
        self.logger.debug("Nothing to acquire for the migration.")

    async def run(self) -> None:
        """Apply every migration."""
        await self.service.upgrade()
        self.logger.info("Migrated the schema.")

    async def close(self) -> None:
        """Release nothing: the service closes its own connection."""
        self.logger.debug("Nothing to release for the migration.")

    async def execute(self) -> AsyncIterator[RunnableStatus]:
        """Run the migration, turning a storage error into ``exit_code`` 1.

        Yields:
            RunnableStatus: The statuses of the base class, without ``EXECUTED`` when the migration failed.
        """
        try:
            async for status in super().execute():
                yield status
        except SEStorageError as error:
            self.exit_code = 1
            self.logger.error("The migration failed with %s.", type(error).__name__)
