from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_live.service.live_hub import LiveHub
from swarm_live.service.live_mailbox import LiveMailbox
from swarm_live.service.live_source import LiveSource
from swarm_models.live.live_subscription import LiveSubscription


class HubLiveSource(LiveSource):
    """A live source backed by a ``LiveHub`` keyed by topic.

    Attributes:
        hub (LiveHub): The hub the producers publish to.
        logger (Logger): Logger instance.
    """

    def __init__(self, hub: LiveHub, logger: Optional[Logger] = None) -> None:
        """Initialise the source.

        Args:
            hub (LiveHub): The hub the producers publish to.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.hub = hub

    ############################
    # Publicly Exposed Methods #
    ############################

    async def join(self, subscription: LiveSubscription) -> LiveMailbox:
        """Subscribe the hub under the topic.

        Args:
            subscription (LiveSubscription): What the client asked.

        Returns:
            LiveMailbox: The client's own mailbox.
        """
        mailbox, first = self.hub.subscribe(subscription.topic)
        if first:
            self.logger.debug("Joined %s as its first watcher.", subscription.topic)
        else:
            self.logger.debug("Joined %s.", subscription.topic)
        return mailbox

    async def leave(self, subscription: LiveSubscription, mailbox: LiveMailbox) -> None:
        """Unsubscribe the mailbox from the topic.

        Args:
            subscription (LiveSubscription): What the client had asked.
            mailbox (LiveMailbox): The mailbox given by ``join``.
        """
        last = self.hub.unsubscribe(subscription.topic, mailbox)
        if last:
            self.logger.debug("Left %s as its last watcher.", subscription.topic)
        else:
            self.logger.debug("Left %s.", subscription.topic)
