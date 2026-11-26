from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from types import TracebackType
from typing import ClassVar, Optional, Self, Type
from uuid import UUID

# Third-party imports
import asyncpg
from asyncpg.pool import PoolConnectionProxy
from asyncpg.transaction import Transaction

# First-party imports
from swarm_models.storage.exceptions import SEStorageNotOpenError


class UnitOfWork:
    """One business operation, sharing one transaction.

    Attributes:
        OPERATOR_SETTING (str): The session setting that row-level security compares with ``operator_id``.
        SET_SETTING_QUERY (str): The query that sets a setting for the current transaction only.
        pool (asyncpg.Pool): The pool the connection comes from.
        operator_id (Optional[UUID]): The Operator the work is done for, or none.
        logger (Logger): Logger instance.
        active_connection (Optional[PoolConnectionProxy[asyncpg.Record]]): The connection held inside the block.
        transaction (Optional[Transaction]): The transaction held inside the block.

    Notes:
        - **The setting is transaction-local**, because PgBouncer runs in transaction mode and a session setting
          would leak into another client.
        - A unit of work without an Operator sets nothing, so row-level security matches no row.
        - The transaction commits on a normal exit and rolls back when the block raises.
    """

    OPERATOR_SETTING: ClassVar[str] = "swarm.operator_id"
    SET_SETTING_QUERY: ClassVar[str] = "SELECT set_config($1, $2, true)"

    def __init__(self, pool: asyncpg.Pool, operator_id: Optional[UUID], logger: Optional[Logger] = None) -> None:
        """Prepare a unit of work.

        Args:
            pool (asyncpg.Pool): The pool to take a connection from.
            operator_id (Optional[UUID]): The Operator the work is done for, or none.
            logger (Optional[Logger]): Logger instance.
        """
        self.pool = pool
        self.operator_id = operator_id
        self.logger = logger if logger else getLogger(__name__)
        self.active_connection: Optional[PoolConnectionProxy[asyncpg.Record]] = None
        self.transaction: Optional[Transaction] = None

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def connection(self) -> PoolConnectionProxy[asyncpg.Record]:
        """Return the connection of the open transaction.

        Returns:
            PoolConnectionProxy[asyncpg.Record]: The connection.

        Raises:
            SEStorageNotOpenError: If the block is not entered.
        """
        if self.active_connection is None:
            self.logger.error("The unit of work has no open transaction.")
            raise SEStorageNotOpenError("The unit of work is not open. Use it inside an async with block.")
        return self.active_connection

    async def __aenter__(self) -> Self:
        """Take a connection, begin the transaction and set the Operator.

        Returns:
            UnitOfWork: This unit of work.

        Raises:
            asyncpg.PostgresError: If the database refuses the transaction or the setting.
            OSError: If the connection fails.
        """
        connection = await self.pool.acquire()
        try:
            transaction = connection.transaction()
            await transaction.start()
            self.transaction = transaction
            if self.operator_id is not None:
                await connection.execute(self.SET_SETTING_QUERY, self.OPERATOR_SETTING, str(self.operator_id))
                self.logger.debug("Operator set for the transaction.")
            else:
                self.logger.debug("No Operator: the transaction sets nothing.")
        except (asyncpg.PostgresError, asyncpg.InterfaceError, OSError) as error:
            self.logger.error("The transaction could not begin: %s.", type(error).__name__)
            await self.pool.release(connection)
            self.transaction = None
            raise
        self.active_connection = connection
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Commit or roll back, then give the connection back.

        Args:
            exc_type (Optional[Type[BaseException]]): The type of the error raised by the block, if any.
            exc_value (Optional[BaseException]): The error raised by the block, if any.
            traceback (Optional[TracebackType]): Its traceback.

        Raises:
            asyncpg.PostgresError: If the commit fails.
        """
        connection = self.active_connection
        transaction = self.transaction
        self.active_connection = None
        self.transaction = None
        if connection is None or transaction is None:
            self.logger.debug("Nothing to close: the unit of work was not open.")
            return
        try:
            if exc_type is None:
                await transaction.commit()
                self.logger.debug("Transaction committed.")
            else:
                await transaction.rollback()
                self.logger.debug("Transaction rolled back after %s.", exc_type.__name__)
        except (asyncpg.PostgresError, asyncpg.InterfaceError, OSError) as error:
            self.logger.error("The transaction could not end: %s.", type(error).__name__)
            raise
        finally:
            await self.pool.release(connection)
