from __future__ import annotations

# Standard library imports
import os
from logging import Logger, getLogger
from typing import Optional
from uuid import UUID

# Third-party imports
import asyncpg

# First-party imports
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_models.storage.exceptions import (
    SEStorageConnectionError,
    SEStorageDsnMissingError,
    SEStorageNotOpenError,
)
from swarm_storage.shared.postgres.unit_of_work import UnitOfWork


class PostgresPool:
    """A small asyncpg pool, and the units of work taken from it.

    Attributes:
        config (PostgresConfig): The pool settings.
        logger (Logger): Logger instance.
        pool (Optional[asyncpg.Pool]): The open pool, none while closed.

    Notes:
        **The DSN is read from the environment entry named by ``config.dsn_key`` and is never logged or quoted.**
    """

    def __init__(self, config: PostgresConfig, logger: Optional[Logger] = None) -> None:
        """Prepare a closed pool.

        Args:
            config (PostgresConfig): The pool settings.
            logger (Optional[Logger]): Logger instance.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)
        self.pool: Optional[asyncpg.Pool] = None

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def is_open(self) -> bool:
        """Tell whether the pool is open.

        Returns:
            bool: True once ``open`` succeeded and ``close`` was not called.
        """
        return self.pool is not None

    async def open(self) -> None:
        """Open the pool.

        Raises:
            SEStorageDsnMissingError: If the environment entry is not set.
            SEStorageConnectionError: If the database cannot be reached.
        """
        if self.pool is not None:
            self.logger.debug("The pool is already open.")
            return
        dsn = os.environ.get(self.config.dsn_key)
        if not dsn:
            self.logger.error("The environment entry %s is not set.", self.config.dsn_key)
            raise SEStorageDsnMissingError(f"The environment entry {self.config.dsn_key} is not set.")
        try:
            self.pool = await asyncpg.create_pool(
                dsn,
                min_size=self.config.pool_min_size,
                max_size=self.config.pool_max_size,
                command_timeout=self.config.command_timeout_s,
            )
        except (OSError, asyncpg.PostgresError, asyncpg.InterfaceError, TimeoutError) as error:
            self.logger.error("The pool could not open: %s.", type(error).__name__)
            raise SEStorageConnectionError(f"Cannot connect to PostgreSQL: {type(error).__name__}.") from error
        self.logger.info("Pool opened with %d to %d connections.", self.config.pool_min_size, self.config.pool_max_size)

    async def close(self) -> None:
        """Close the pool, safely before ``open`` and when called twice."""
        pool = self.pool
        self.pool = None
        if pool is None:
            self.logger.debug("The pool is not open: nothing to close.")
            return
        try:
            await pool.close()
        except (OSError, asyncpg.PostgresError, asyncpg.InterfaceError) as error:
            self.logger.error("The pool could not close cleanly: %s.", type(error).__name__)
            raise
        self.logger.info("Pool closed.")

    def unit_of_work(self, operator_id: Optional[UUID]) -> UnitOfWork:
        """Create a unit of work on this pool.

        Args:
            operator_id (Optional[UUID]): The Operator the work is done for, or none.

        Returns:
            UnitOfWork: A unit of work, to enter with ``async with``.

        Raises:
            SEStorageNotOpenError: If the pool is not open.
        """
        if self.pool is None:
            self.logger.error("A unit of work was asked of a closed pool.")
            raise SEStorageNotOpenError("The pool is not open. Call open first.")
        return UnitOfWork(self.pool, operator_id)
