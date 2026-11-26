from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod

# First-party imports
from swarm_live.service.live_mailbox import LiveMailbox
from swarm_models.live.live_subscription import LiveSubscription


class LiveSource(ABC):
    """Where a live session gets the frames of the topics its client follows.

    Notes:
        - The gateway reads them from NATS and the flight
          engine from its own loop, both through a subclass.
    """

    @abstractmethod
    async def join(self, subscription: LiveSubscription) -> LiveMailbox:
        """Start following a topic.

        Args:
            subscription (LiveSubscription): What the client asked.

        Returns:
            LiveMailbox: The mailbox that holds the latest frame of the topic.
        """

    @abstractmethod
    async def leave(self, subscription: LiveSubscription, mailbox: LiveMailbox) -> None:
        """Stop following a topic.

        Args:
            subscription (LiveSubscription): What the client had asked.
            mailbox (LiveMailbox): The mailbox given by ``join``.
        """
