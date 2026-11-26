from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Callable, Dict, List, Optional

# Third-party imports
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.aio.subscription import Subscription
from nats.errors import Error as NatsError

# First-party imports
from swarm_models.live.feed.exceptions import SEMissionFeedError


class MissionFeedClient:
    """Follows NATS subjects of the missions and hands each frame to a handler.

    Attributes:
        client (Client): The connected NATS client.
        subscriptions (Dict[str, Subscription]): The core subscription of each subject.
        handlers (Dict[str, Callable[[str, bytes], None]]): The handler of each subject.
        logger (Logger): Logger instance.

    Notes:
        - One core subscription is made per subject, and every message goes through ``_on_message``.
        - **NATS errors are wrapped** in ``SEMissionFeedError``, so the service catches one type.
        - A frame is handed over as it came, without being decoded.
    """

    def __init__(self, client: Client, logger: Optional[Logger] = None) -> None:
        """Keep the client.

        Args:
            client (Client): The connected NATS client.
            logger (Optional[Logger]): Logger instance.
        """
        self.client = client
        self.logger = logger if logger else getLogger(__name__)
        self.subscriptions: Dict[str, Subscription] = {}
        self.handlers: Dict[str, Callable[[str, bytes], None]] = {}

    ############################
    # Internal Helpers Methods #
    ############################

    async def _on_message(self, msg: Msg) -> None:
        """Dispatch a message to the handler of its subject.

        Args:
            msg (Msg): The message received from NATS.
        """
        handler = self.handlers.get(msg.subject)
        if handler is None:
            self.logger.debug("No handler for %s.", msg.subject)
            return
        handler(msg.subject, msg.data)

    ############################
    # Publicly Exposed Methods #
    ############################

    def subjects(self) -> List[str]:
        """List the subscribed subjects.

        Returns:
            List[str]: The subjects.
        """
        return list(self.subscriptions)

    async def subscribe(self, subject: str, handler: Callable[[str, bytes], None]) -> None:
        """Subscribe to a subject.

        Args:
            subject (str): The subject.
            handler (Callable[[str, bytes], None]): Called with the subject and the raw data of each message.

        Raises:
            SEMissionFeedError: When NATS refuses the subscription.

        Notes:
            - **It returns only once the server holds the subscription:** the flush after ``subscribe`` waits for
              the server, so a frame published right after the first watcher joins is never lost. Core NATS keeps
              nothing for a subject nobody has subscribed to yet.
            - The handler is registered before subscribing, so that a message arriving during the flush finds it.
        """
        if subject in self.subscriptions:
            self.logger.debug("Already subscribed to %s, handler replaced.", subject)
            self.handlers[subject] = handler
            return
        self.handlers[subject] = handler
        try:
            subscription = await self.client.subscribe(subject, cb=self._on_message)
            await self.client.flush()
        except (TimeoutError, NatsError, OSError) as error:
            self.handlers.pop(subject, None)
            self.logger.error("Could not subscribe to %s: %s.", subject, type(error).__name__)
            raise SEMissionFeedError(f"Subscribing to {subject} failed with {type(error).__name__}.") from error
        self.subscriptions[subject] = subscription
        self.logger.info("Subscribed to %s.", subject)

    async def unsubscribe(self, subject: str) -> None:
        """Unsubscribe from a subject.

        Args:
            subject (str): The subject.

        Raises:
            SEMissionFeedError: When NATS refuses the unsubscription.
        """
        subscription = self.subscriptions.pop(subject, None)
        self.handlers.pop(subject, None)
        if subscription is None:
            self.logger.debug("Was not subscribed to %s.", subject)
            return
        try:
            await subscription.unsubscribe()
        except (TimeoutError, NatsError, OSError) as error:
            self.logger.error("Could not unsubscribe from %s: %s.", subject, type(error).__name__)
            raise SEMissionFeedError(f"Unsubscribing from {subject} failed with {type(error).__name__}.") from error
        self.logger.info("Unsubscribed from %s.", subject)
