from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import AsyncIterator, ClassVar, Optional

# First-party imports
from fleet.service.schema.schema_service import SchemaService
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.storage.exceptions import SEStorageError


class MigrateCommand(AsyncRunnable):
    """Applies every migration of the fleet schema, as the pre-deploy step does.

    Attributes:
        EXIT_OK (int): The exit code when the schema is at the latest revision.
        EXIT_FAILED (int): The exit code when the migration could not run.
        schema_service (SchemaService): The service that upgrades the schema.
        exit_code (int): The exit code, read after ``execute``.

    Notes:
        - **``execute`` never raises a storage error**: it logs it, sets ``exit_code`` to ``1`` and ends without
          ``EXECUTED``, so that the entry point only reads the exit code.
    """

    EXIT_OK: ClassVar[int] = 0
    EXIT_FAILED: ClassVar[int] = 1

    def __init__(
        self, status_interval_s: float, schema_service: SchemaService, logger: Optional[Logger] = None
    ) -> None:
        """Initialise the command.

        Args:
            status_interval_s (float): Seconds between two statuses.
            schema_service (SchemaService): The service that upgrades the schema.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.schema_service = schema_service
        self.exit_code = self.EXIT_OK

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Acquire nothing: the migrator opens its own connection."""
        self.logger.debug("Nothing to initialise.")

    async def run(self) -> None:
        """Upgrade the schema to the latest revision."""
        await self.schema_service.upgrade()
        self.exit_code = self.EXIT_OK

    async def close(self) -> None:
        """Release nothing: the migrator closes its own connection."""
        self.logger.debug("Nothing to close.")

    async def execute(self) -> AsyncIterator[RunnableStatus]:
        """Run the base execution, turning a storage error into the exit code ``1``.

        Yields:
            RunnableStatus: The statuses of the base execution, or the last status reached when it failed.
        """
        try:
            async for status in super().execute():
                yield status
        except SEStorageError as error:
            self.logger.error("The migration failed with %s.", type(error).__name__)
            self.exit_code = self.EXIT_FAILED
            yield self.status
