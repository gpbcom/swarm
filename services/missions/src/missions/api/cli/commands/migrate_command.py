from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional

# First-party imports
from missions.service.schema.schema_service import SchemaService
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_storage.models.postgres.exceptions import SEStorageError


class MigrateCommand(AsyncRunnable):
    """Brings the PostgreSQL schema of missions to the latest revision, as a pre-deploy step.

    Attributes:
        EXIT_OK (ClassVar[int]): The exit code when the migration succeeded.
        EXIT_FAILED (ClassVar[int]): The exit code when the migration failed.
        schema (SchemaService): The service that applies the migrations.
        exit_code (int): The exit code, read after ``execute``.

    Notes:
        - **A storage failure is not raised**: it is logged, printed and turned into ``EXIT_FAILED``, so that the
          console script ends with a code the deploy step can read.
    """

    EXIT_OK: ClassVar[int] = 0
    EXIT_FAILED: ClassVar[int] = 1

    def __init__(self, schema: SchemaService, status_interval_s: float, logger: Optional[Logger] = None) -> None:
        """Initialise the command.

        Args:
            schema (SchemaService): The service that applies the migrations.
            status_interval_s (float): Seconds between two statuses, from the configuration.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.schema = schema
        self.exit_code = self.EXIT_OK

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Acquire nothing: the migrator opens its own connection."""
        self.logger.debug("Nothing to initialise.")

    async def run(self) -> None:
        """Apply every migration, and set the exit code."""
        try:
            await self.schema.upgrade()
        except SEStorageError as error:
            self.logger.error("The migration failed with %s.", type(error).__name__)
            print(f"The migration failed: {type(error).__name__}.")
            self.exit_code = self.EXIT_FAILED
            return
        self.logger.info("The migration succeeded.")
        self.exit_code = self.EXIT_OK

    async def close(self) -> None:
        """Release nothing: the command holds no resource."""
        self.logger.debug("Nothing to close.")
