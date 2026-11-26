from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_models.live.session.live_session_config import LiveSessionConfig
from swarm_service.shared.live.factories.live_runnable_factory import LiveRunnableFactory
from swarm_service.shared.live.live_codec import LiveCodec
from swarm_service.shared.live.live_session import LiveSession
from swarm_service.shared.live.live_socket import LiveSocket
from swarm_service.shared.live.sources.live_source import LiveSource


class LiveSessionFactory(LiveRunnableFactory[LiveSession]):
    """Build the ``LiveSession`` of one client socket.

    Attributes:
        socket (LiveSocket): The client socket.
        source (LiveSource): Where the frames of the topics come from.
        codec (LiveCodec): Decodes the client's messages.
        config (LiveSessionConfig): The settings of the session.
        logger (Logger): Logger instance.
    """

    def __init__(
        self,
        socket: LiveSocket,
        source: LiveSource,
        codec: LiveCodec,
        config: LiveSessionConfig,
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the factory.

        Args:
            socket (LiveSocket): The client socket.
            source (LiveSource): Where the frames of the topics come from.
            codec (LiveCodec): Decodes the client's messages.
            config (LiveSessionConfig): The settings of the session.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.socket = socket
        self.source = source
        self.codec = codec
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> LiveSession:
        """Build one session.

        Returns:
            LiveSession: A new session, not started.
        """
        self.logger.debug("Building a live session.")
        return LiveSession(self.socket, self.source, self.codec, self.config)
