from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Awaitable, Callable, Optional, Type

# Third-party imports
from nats.aio.client import Client
from pydantic import BaseModel

# First-party imports
from swarm_nats.api.bus.nats_responder import NatsResponder
from swarm_nats.api.factories.bus_runnable_factory import BusRunnableFactory
from swarm_nats.models.config.nats_responder_config import NatsResponderConfig


class NatsResponderFactory[Q: BaseModel, R: BaseModel](BusRunnableFactory[NatsResponder[Q, R]]):
    """Build the ``NatsResponder`` of one subject.

    Attributes:
        connection (Client): The connected NATS client.
        config (NatsResponderConfig): The settings of the responder.
        request_type (Type[Q]): The model of the request body.
        handler (Callable[[Q], Awaitable[R]]): The coroutine that answers one request.
        logger (Logger): Logger instance.
    """

    def __init__(
        self,
        connection: Client,
        config: NatsResponderConfig,
        request_type: Type[Q],
        handler: Callable[[Q], Awaitable[R]],
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the factory.

        Args:
            connection (Client): The connected NATS client.
            config (NatsResponderConfig): The settings of the responder.
            request_type (Type[Q]): The model of the request body.
            handler (Callable[[Q], Awaitable[R]]): The coroutine that answers one request.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.connection = connection
        self.config = config
        self.request_type = request_type
        self.handler = handler

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> NatsResponder[Q, R]:
        """Build one responder.

        Returns:
            NatsResponder[Q, R]: A new responder, not started.
        """
        self.logger.debug("Building a responder for %s.", self.config.subject)
        return NatsResponder(self.connection, self.config, self.request_type, self.handler)
