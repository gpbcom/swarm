from __future__ import annotations

# Standard library imports
from logging import Logger
from typing import Awaitable, Callable, Optional, Type

# Third-party imports
from nats.aio.client import Client
from pydantic import BaseModel

# First-party imports
from swarm_nats.api.bus.durable_consumer import DurableConsumer
from swarm_nats.api.factories.bus_runnable_factory import BusRunnableFactory
from swarm_nats.models.config.durable_consumer_config import DurableConsumerConfig


class DurableConsumerFactory[M: BaseModel](BusRunnableFactory[DurableConsumer[M]]):
    """Factory of durable JetStream consumers.

    Attributes:
        connection (Client): The NATS connection the consumers read from.
        config (DurableConsumerConfig): The settings of the durable consumers.
        message_type (Type[M]): The model each message is decoded into.
        handler (Callable[[M], Awaitable[None]]): What is done with each decoded message.
    """

    def __init__(
        self,
        connection: Client,
        config: DurableConsumerConfig,
        message_type: Type[M],
        handler: Callable[[M], Awaitable[None]],
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the factory.

        Args:
            connection (Client): The NATS connection the consumers read from.
            config (DurableConsumerConfig): The settings of the durable consumers.
            message_type (Type[M]): The model each message is decoded into.
            handler (Callable[[M], Awaitable[None]]): What is done with each decoded message.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__(logger)
        self.connection = connection
        self.config = config
        self.message_type = message_type
        self.handler = handler

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> DurableConsumer[M]:
        """Build one durable consumer.

        Returns:
            DurableConsumer[M]: A new consumer that is not started.
        """
        return DurableConsumer(self.connection, self.config, self.message_type, self.handler, self.logger)
