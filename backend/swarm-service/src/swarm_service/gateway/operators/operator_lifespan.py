from __future__ import annotations

# Standard library imports
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from logging import Logger, getLogger
from typing import AsyncIterator, Callable, Optional

# Third-party imports
from fastapi import FastAPI

# First-party imports
from swarm_service.gateway.operators.operator_service import OperatorService


class OperatorLifespan:
    """Closes the Operator service when the gateway application ends, around the lifespan it already had.

    Attributes:
        service (OperatorService): The service to close.
        inner (Callable[[FastAPI], AbstractAsyncContextManager[None]]): The lifespan that was installed before.
        logger (Logger): Logger instance.

    Notes:
        - The inner lifespan is entered first and left first, then the service is closed.
        - **The service is closed also when the block raises**, so the pool never outlives the application.
    """

    def __init__(
        self,
        service: OperatorService,
        inner: Callable[[FastAPI], AbstractAsyncContextManager[None]],
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the lifespan.

        Args:
            service (OperatorService): The service to close.
            inner (Callable[[FastAPI], AbstractAsyncContextManager[None]]): The lifespan that was installed before.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.service = service
        self.inner = inner

    ############################
    # Publicly Exposed Methods #
    ############################

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        """Run the inner lifespan, then close the service.

        Args:
            app (FastAPI): The application.

        Yields:
            None: While the application serves.
        """
        try:
            async with self.inner(app):
                self.logger.debug("The inner lifespan is entered.")
                yield
        except BaseException:
            self.logger.error("The application stopped with an error.")
            raise
        finally:
            await self.service.close()
            self.logger.info("The Operator service is closed.")
