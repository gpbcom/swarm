from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import TYPE_CHECKING, Optional
from uuid import UUID

# First-party imports
from swarm_models.live.live_subscription import LiveSubscription

from swarm_live.service.live_mailbox import LiveMailbox  # isort: skip
from swarm_live.service.live_source import LiveSource  # isort: skip

if TYPE_CHECKING:
    from swarm_service.gateway.live.live_fan_out import LiveFanOut


class OperatorLiveSource(LiveSource):
    """The live source of one connection: it joins the fan-out under the Operator of that connection only.

    Attributes:
        operator_id (UUID): The Operator of the connection, never taken from the client.
        fan_out (LiveFanOut): The fan-out shared by every connection.
        logger (Logger): Logger instance.

    Notes:
        - **The fan-out is typed behind ``TYPE_CHECKING``**, because ``LiveFanOut`` builds this class and the two
          modules would otherwise import each other.
    """

    def __init__(self, operator_id: UUID, fan_out: LiveFanOut, logger: Optional[Logger] = None) -> None:
        """Keep the Operator and the fan-out.

        Args:
            operator_id (UUID): The Operator of the connection.
            fan_out (LiveFanOut): The fan-out shared by every connection.
            logger (Optional[Logger]): Logger instance.
        """
        self.operator_id = operator_id
        self.fan_out = fan_out
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def join(self, subscription: LiveSubscription) -> LiveMailbox:
        """Start following a topic of the Operator.

        Args:
            subscription (LiveSubscription): What the client asked.

        Returns:
            LiveMailbox: The mailbox that holds the latest frame of the topic.
        """
        self.logger.debug("Operator %s joins %s.", self.operator_id, subscription.topic)
        return await self.fan_out.join(self.operator_id, subscription)

    async def leave(self, subscription: LiveSubscription, mailbox: LiveMailbox) -> None:
        """Stop following a topic of the Operator.

        Args:
            subscription (LiveSubscription): What the client had asked.
            mailbox (LiveMailbox): The mailbox given by ``join``.
        """
        self.logger.debug("Operator %s leaves %s.", self.operator_id, subscription.topic)
        await self.fan_out.leave(self.operator_id, subscription, mailbox)
