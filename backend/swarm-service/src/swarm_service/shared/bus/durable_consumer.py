from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Awaitable, Callable, List, Optional, Type

# Third-party imports
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.errors import TimeoutError as NatsTimeoutError
from nats.js.api import AckPolicy, ConsumerConfig
from nats.js.client import JetStreamContext
from pydantic import BaseModel, ValidationError

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.config.nats.durable_consumer_config import DurableConsumerConfig


class DurableConsumer[M: BaseModel](AsyncRunnable):
    """A durable JetStream pull consumer that decodes each message and gives it to a handler.

    Attributes:
        connection (Client): The NATS connection to read from.
        config (DurableConsumerConfig): The settings of the durable consumer.
        message_type (Type[M]): The model each message is decoded into.
        handler (Callable[[M], Awaitable[None]]): What is done with each decoded message.
        subscription (Optional[JetStreamContext.PullSubscription]): The pull subscription, set by ``initialize``.

    Notes:
        - **Delivery is at least once, and handlers must be idempotent by event id.** The publisher's ``Nats-Msg-Id``
          header deduplicates what is published, and the explicit acknowledgement comes after the handler, so a message
          whose handler failed or whose acknowledgement was lost is delivered again.
        - A message that does not decode is terminated, so the server never redelivers it.
        - ``close`` only drops the subscription: the durable consumer stays on the server, so a new consumer with the
          same name resumes after the last acknowledged message.
        - The broad ``except`` is around the handler only, because any failure of the handler must be reported and
          answered with a negative acknowledgement.
    """

    def __init__(
        self,
        connection: Client,
        config: DurableConsumerConfig,
        message_type: Type[M],
        handler: Callable[[M], Awaitable[None]],
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the consumer.

        Args:
            connection (Client): The NATS connection to read from.
            config (DurableConsumerConfig): The settings of the durable consumer.
            message_type (Type[M]): The model each message is decoded into.
            handler (Callable[[M], Awaitable[None]]): What is done with each decoded message.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.connection = connection
        self.config = config
        self.message_type = message_type
        self.handler = handler
        self.subscription: Optional[JetStreamContext.PullSubscription] = None

    ############################
    # Internal Helpers Methods #
    ############################

    async def _handle(self, message: Msg) -> None:
        """Decode one message, give it to the handler, then acknowledge it, refuse it or terminate it.

        Args:
            message (Msg): The message that was fetched.
        """
        try:
            decoded = self.message_type.model_validate_json(message.data)
        except ValidationError as error:
            self.logger.error(
                "Terminated a message of %s that is not a %s: %s.",
                self.config.durable_name,
                self.message_type.__name__,
                type(error).__name__,
            )
            await message.term()
            return
        try:
            await self.handler(decoded)
        except Exception as error:  # noqa: BLE001
            self.logger.error(
                "The handler of %s failed with %s, so the message is delivered again.",
                self.config.durable_name,
                type(error).__name__,
            )
            await message.nak()
            return
        await message.ack()
        self.logger.debug("Acknowledged a message of %s.", self.config.durable_name)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Create or bind the durable pull consumer."""
        journal = self.connection.jetstream()
        consumer_config = ConsumerConfig(
            durable_name=self.config.durable_name,
            ack_policy=AckPolicy.EXPLICIT,
            ack_wait=self.config.ack_wait_s,
            max_deliver=self.config.max_deliver,
            filter_subject=self.config.filter_subject,
        )
        await journal.add_consumer(self.config.stream, consumer_config)
        self.subscription = await journal.pull_subscribe_bind(self.config.durable_name, self.config.stream)
        self.logger.info("Bound the durable consumer %s on %s.", self.config.durable_name, self.config.stream)

    async def run(self) -> None:
        """Fetch and handle messages until the task is cancelled."""
        if self.subscription is None:
            self.logger.error("The consumer %s ran before it was initialised.", self.config.durable_name)
            raise RuntimeError("The consumer must be initialised before it runs.")
        while True:
            try:
                messages: List[Msg] = await self.subscription.fetch(
                    self.config.batch_size, timeout=self.config.fetch_timeout_s
                )
            except NatsTimeoutError:
                self.logger.debug("Nothing to read from %s yet.", self.config.durable_name)
                continue
            self.logger.debug("Fetched %d messages for %s.", len(messages), self.config.durable_name)
            for message in messages:
                await self._handle(message)

    async def close(self) -> None:
        """Drop the subscription and keep the durable consumer on the server."""
        if self.subscription is None:
            self.logger.debug("No subscription of %s to close.", self.config.durable_name)
            return
        await self.subscription.unsubscribe()
        self.subscription = None
        self.logger.info("Closed the subscription of %s.", self.config.durable_name)
