from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Optional
from uuid import UUID

# Third-party imports
from nats.aio.client import Client

# First-party imports
from swarm_clients.gateway.nats.mission_feed_client import MissionFeedClient
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.live.feed.exceptions import SELiveFeedNotReadyError
from swarm_models.live.feed.live_config import LiveConfig
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_service.gateway.live.live_fan_out import LiveFanOut
from swarm_service.gateway.live.operator_live_source import OperatorLiveSource

from swarm_live.service.live_hub import LiveHub  # isort: skip


class LiveFeed(AsyncRunnable):
    """Connects the gateway to NATS and serves the live sources of its client connections.

    Attributes:
        config (LiveConfig): The configuration of the live feed.
        connector (NatsConnector): Opens and closes the NATS connection.
        hub (LiveHub): The hub the frames are fanned out through.
        client (Optional[Client]): The NATS connection, while the feed is initialised.
        fan_out (Optional[LiveFanOut]): The fan-out, while the feed is initialised.
        stopped (asyncio.Event): Set by ``close`` to end ``run``.
        logger (Logger): Logger instance.

    Notes:
        - ``run`` blocks until ``close``: the work is done by the NATS handlers and the client sessions.
        - **``close`` is safe after a partial ``initialize``**, and after a previous ``close``.
        - **A closed feed refuses a source**, so no client can join a connection that is gone.
    """

    def __init__(
        self, config: LiveConfig, connector: NatsConnector, hub: LiveHub, logger: Optional[Logger] = None
    ) -> None:
        """Keep the parts, connected to nothing yet.

        Args:
            config (LiveConfig): The configuration of the live feed.
            connector (NatsConnector): Opens and closes the NATS connection.
            hub (LiveHub): The hub the frames are fanned out through.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.connector = connector
        self.hub = hub
        self.client: Optional[Client] = None
        self.fan_out: Optional[LiveFanOut] = None
        self.stopped = asyncio.Event()

    ############################
    # Publicly Exposed Methods #
    ############################

    def source_for(self, operator_id: UUID) -> OperatorLiveSource:
        """Give the live source of one Operator.

        Args:
            operator_id (UUID): The Operator of the connection.

        Returns:
            OperatorLiveSource: A source that joins under that Operator only.

        Raises:
            SELiveFeedNotReadyError: If the feed is not initialised or is closed.
        """
        if self.fan_out is None:
            self.logger.error("A live source was asked of a feed that is not ready.")
            raise SELiveFeedNotReadyError("The live feed is not initialised or is closed.")
        return self.fan_out.source_for(operator_id)

    async def initialize(self) -> None:
        """Connect to NATS and build the fan-out.

        Raises:
            SENatsConnectionError: If NATS cannot be reached.
        """
        self.client = await self.connector.connect()
        self.fan_out = LiveFanOut(self.hub, MissionFeedClient(self.client))
        self.logger.info("Live feed initialised.")

    async def run(self) -> None:
        """Serve until the feed is closed."""
        self.logger.debug("Live feed serving.")
        await self.stopped.wait()

    async def close(self) -> None:
        """Refuse new sources and disconnect from NATS, safely before ``initialize`` and when called twice.

        Raises:
            SENatsConnectionError: If the connection cannot be drained.
        """
        self.fan_out = None
        self.stopped.set()
        client = self.client
        self.client = None
        if client is None:
            self.logger.debug("Live feed had no connection to close.")
            return
        try:
            await self.connector.disconnect(client)
        except Exception as error:
            self.logger.error("Could not close the live feed: %s.", type(error).__name__)
            raise
        self.logger.info("Live feed closed.")
