from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_models.live.feed.live_config import LiveConfig
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_service.gateway.factories.live_service_factory import LiveServiceFactory
from swarm_service.gateway.live.live_feed import LiveFeed
from swarm_service.shared.live.hub.live_hub import LiveHub


class LiveFeedFactory(LiveServiceFactory[LiveFeed]):
    """Builds the live feed of the gateway from its configuration.

    Attributes:
        config (LiveConfig): The configuration of the live feed.
        logger (Logger): Logger instance.
    """

    def __init__(self, config: LiveConfig, logger: Optional[Logger] = None) -> None:
        """Prepare the factory.

        Args:
            config (LiveConfig): The configuration of the live feed.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> LiveFeed:
        """Build one live feed with its own connector and hub, not connected yet.

        Returns:
            LiveFeed: A new feed.
        """
        self.logger.debug("Building a live feed.")
        return LiveFeed(self.config, NatsConnector(self.config.nats), LiveHub())
