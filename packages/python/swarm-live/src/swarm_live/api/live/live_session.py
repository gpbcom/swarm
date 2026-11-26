from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Dict, Optional, Tuple

# Third-party imports
from starlette.websockets import WebSocketDisconnect

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_live.api.live.live_socket import LiveSocket
from swarm_live.models.config.live_session_config import LiveSessionConfig
from swarm_live.models.exceptions import SELiveMessageUnreadable
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_mailbox import LiveMailbox
from swarm_live.service.live_source import LiveSource
from swarm_models.models.live.live_subscription import LiveSubscription


class LiveSession(AsyncRunnable):
    """Serve one client socket: read its subscriptions and send it the latest frame of each topic.

    Attributes:
        socket (LiveSocket): The client socket.
        source (LiveSource): Where the frames of the topics come from.
        codec (LiveCodec): Decodes the client's messages.
        config (LiveSessionConfig): The settings of the session.
        sent (int): How many frames were sent to the client.
        joined (Dict[str, Tuple[LiveSubscription, LiveMailbox, asyncio.Task[None]]]): The topics followed, each with
            its mailbox and its sender.
        write_lock (asyncio.Lock): Makes the senders write to the socket one frame at a time.
        logger (Logger): Logger instance.

    Notes:
        - One sender per topic takes from its mailbox and writes at the pace of the client, so frames never queue:
          **a slow client skips intermediate frames and always gets the latest one**.
        - The session ends when the socket raises ``WebSocketDisconnect``, and ``close`` leaves every topic.
        - An unreadable message is logged at ``WARNING`` and ignored.
    """

    def __init__(
        self,
        socket: LiveSocket,
        source: LiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the session.

        Args:
            socket (LiveSocket): The client socket.
            source (LiveSource): Where the frames of the topics come from.
            codec (LiveCodec): Decodes the client's messages.
            config (LiveSessionConfig): The settings of the session.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.socket = socket
        self.source = source
        self.codec = codec
        self.config = config
        self.sent = 0
        self.joined: Dict[str, Tuple[LiveSubscription, LiveMailbox, asyncio.Task[None]]] = {}
        self.write_lock = asyncio.Lock()

    ############################
    # Internal Helpers Methods #
    ############################

    async def _send_loop(self, mailbox: LiveMailbox) -> None:
        """Send every frame of a mailbox to the client, one at a time.

        Args:
            mailbox (LiveMailbox): The mailbox of one topic.
        """
        while True:
            data = await mailbox.take()
            try:
                async with self.write_lock:
                    await self.socket.send_bytes(data)
            except WebSocketDisconnect:
                self.logger.debug("The client left while a frame was sent.")
                return
            self.sent += 1
            self.logger.debug("Sent frame %d of %d bytes.", self.sent, len(data))

    async def _subscribe(self, data: bytes) -> None:
        """Read one message of the client and join the topic it asks for.

        Args:
            data (bytes): The message.
        """
        try:
            subscription = self.codec.decode_subscription(data)
        except SELiveMessageUnreadable as error:
            self.logger.warning("Ignored an unreadable message: %s.", type(error).__name__)
            return
        if subscription.topic in self.joined:
            self.logger.debug("Already following %s.", subscription.topic)
            return
        mailbox = await self.source.join(subscription)
        sender = asyncio.create_task(self._send_loop(mailbox))
        self.joined[subscription.topic] = (subscription, mailbox, sender)
        self.logger.info("Following %s.", subscription.topic)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Start with no topic: the client subscribes with its first messages."""
        self.logger.debug("Live session ready.")

    async def run(self) -> None:
        """Read the client's messages until it disconnects."""
        while True:
            try:
                data = await self.socket.receive_bytes()
            except WebSocketDisconnect:
                self.logger.info("The client disconnected after %d frames.", self.sent)
                return
            await self._subscribe(data)

    async def close(self) -> None:
        """Stop every sender and leave every topic."""
        joined = list(self.joined.values())
        self.joined.clear()
        for subscription, mailbox, sender in joined:
            sender.cancel()
            try:
                await sender
            except asyncio.CancelledError:
                self.logger.debug("Stopped the sender of %s.", subscription.topic)
            await self.source.leave(subscription, mailbox)
            self.logger.debug("Left %s.", subscription.topic)
