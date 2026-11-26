from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional

# Third-party imports
import nats
from nats.aio.client import Client
from nats.errors import Error as NatsError

# First-party imports
from swarm_nats.models.bus.exceptions import SENatsConnectionError
from swarm_nats.models.config.nats_client_config import NatsClientConfig


class NatsConnector:
    """Opens and closes the connection of a service to NATS.

    Attributes:
        MAX_RECONNECT_KEY (ClassVar[str]): The option of the client that bounds its reconnection attempts.
        FIRST_CONNECT_ATTEMPTS (ClassVar[int]): The retries allowed to the first connection.
        RECONNECT_ATTEMPTS (ClassVar[int]): The reconnection attempts once connected, the default of nats-py.
        config (NatsClientConfig): The settings of the connection.
        logger (Logger): Logger instance.

    Notes:
        - ``credentials_path`` is a name: the content of the credentials file is never read here nor logged.
        - **The first connection is allowed one retry only**, because nats-py otherwise retries a refused first
          connection about sixty times. The usual bound is restored once the client is connected.
        - **A credentials file that does not exist is refused up front**, because a server that asks for no
          authentication would otherwise never read it and the mistake would go unnoticed.
        - **Any connection failure is a ``SENatsConnectionError``**, so callers catch one type.
    """

    MAX_RECONNECT_KEY: ClassVar[str] = "max_reconnect_attempts"
    FIRST_CONNECT_ATTEMPTS: ClassVar[int] = 1
    RECONNECT_ATTEMPTS: ClassVar[int] = 60

    def __init__(self, config: NatsClientConfig, logger: Optional[Logger] = None) -> None:
        """Keep the settings.

        Args:
            config (NatsClientConfig): The settings of the connection.
            logger (Optional[Logger]): Logger instance.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    async def _on_error(self, error: Exception) -> None:
        """Log an error reported by the client.

        Args:
            error (Exception): The error.
        """
        self.logger.error("NATS client error: %s.", type(error).__name__)

    async def _on_disconnected(self) -> None:
        """Log the loss of the connection."""
        self.logger.warning("Disconnected from NATS.")

    async def _on_reconnected(self) -> None:
        """Log the return of the connection."""
        self.logger.info("Reconnected to NATS.")

    ############################
    # Publicly Exposed Methods #
    ############################

    async def connect(self) -> Client:
        """Open a connection.

        Returns:
            Client: The connected client.

        Raises:
            SENatsConnectionError: When the connection cannot be opened.
        """
        self.logger.debug("Connecting to %d NATS server(s).", len(self.config.servers))
        credentials_path = self.config.credentials_path
        if credentials_path is not None and not Path(credentials_path).is_file():
            self.logger.error("The credentials file is missing.")
            raise SENatsConnectionError(f"Invalid credentials_path: {credentials_path!r}. The file does not exist.")
        self.logger.debug("The credentials file is present or not needed.")
        try:
            client = await nats.connect(
                max_reconnect_attempts=self.FIRST_CONNECT_ATTEMPTS,
                servers=self.config.servers,
                name=self.config.name,
                connect_timeout=self.config.connect_timeout_s,
                reconnect_time_wait=self.config.reconnect_wait_s,
                user_credentials=self.config.credentials_path,
                error_cb=self._on_error,
                disconnected_cb=self._on_disconnected,
                reconnected_cb=self._on_reconnected,
            )
        except (TimeoutError, NatsError, OSError) as error:
            self.logger.error("Could not connect to NATS: %s.", type(error).__name__)
            raise SENatsConnectionError(f"The connection to NATS failed with {type(error).__name__}.") from error
        client.options[self.MAX_RECONNECT_KEY] = self.RECONNECT_ATTEMPTS
        self.logger.info("Connected to NATS as %s.", self.config.name)
        return client

    async def disconnect(self, client: Client) -> None:
        """Drain and close a connection.

        Args:
            client (Client): The client to close.

        Raises:
            SENatsConnectionError: When the client cannot be drained.
        """
        if client.is_closed:
            self.logger.debug("The NATS client is already closed.")
            return
        try:
            await client.drain()
        except (TimeoutError, NatsError, OSError) as error:
            self.logger.error("Could not drain the NATS client: %s.", type(error).__name__)
            raise SENatsConnectionError(f"Draining NATS failed with {type(error).__name__}.") from error
        self.logger.info("Disconnected from NATS.")
