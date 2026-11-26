from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import List, Optional
from uuid import UUID

# First-party imports
from swarm_clients.gateway.nats.mission_feed_client import MissionFeedClient
from swarm_models.live.feed.exceptions import SEMissionFeedError
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.subjects.operator_subjects import OperatorSubjects
from swarm_service.gateway.live.operator_live_source import OperatorLiveSource
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.hub.live_mailbox import LiveMailbox


class LiveFanOut:
    """Subscribes once per Mission subject to NATS and fans the frames out to every client watching it.

    Attributes:
        hub (LiveHub): The hub keyed by NATS subject, with one mailbox per client.
        feed (MissionFeedClient): The NATS side.
        logger (Logger): Logger instance.

    Notes:
        - **The Operator always comes from the connection**: the hub key is built with it, so a client never reaches
          the subject of another Operator.
        - NATS is subscribed on the first watcher of a subject and unsubscribed on the last.
        - A frame is published into the hub as raw bytes, without being decoded.
    """

    def __init__(self, hub: LiveHub, feed: MissionFeedClient, logger: Optional[Logger] = None) -> None:
        """Keep the hub and the NATS client.

        Args:
            hub (LiveHub): The hub keyed by NATS subject.
            feed (MissionFeedClient): The NATS side.
            logger (Optional[Logger]): Logger instance.
        """
        self.hub = hub
        self.feed = feed
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _subject(self, operator_id: UUID, subscription: LiveSubscription) -> str:
        """Give the NATS subject of a subscription of an Operator.

        Args:
            operator_id (UUID): The Operator of the connection.
            subscription (LiveSubscription): What the client asked.

        Returns:
            str: The subject.
        """
        return OperatorSubjects(operator_id=operator_id).mission(subscription.mission(), subscription.kind())

    ############################
    # Publicly Exposed Methods #
    ############################

    def subjects(self) -> List[str]:
        """List the subjects subscribed on NATS.

        Returns:
            List[str]: The subjects.
        """
        return self.feed.subjects()

    def source_for(self, operator_id: UUID) -> OperatorLiveSource:
        """Give the live source of one Operator.

        Args:
            operator_id (UUID): The Operator of the connection.

        Returns:
            OperatorLiveSource: A source that joins under that Operator only.
        """
        self.logger.debug("Giving a live source to Operator %s.", operator_id)
        return OperatorLiveSource(operator_id, self)

    def deliver(self, subject: str, data: bytes) -> None:
        """Put a frame received from NATS in the mailboxes of the clients of its subject.

        Args:
            subject (str): The NATS subject.
            data (bytes): The raw frame.
        """
        self.hub.publish(subject, data)

    async def join(self, operator_id: UUID, subscription: LiveSubscription) -> LiveMailbox:
        """Give a client a mailbox on a topic of its Operator.

        Args:
            operator_id (UUID): The Operator of the connection.
            subscription (LiveSubscription): What the client asked.

        Returns:
            LiveMailbox: The client's mailbox.

        Raises:
            SEMissionFeedError: When NATS refuses the first subscription of the subject.
        """
        subject = self._subject(operator_id, subscription)
        mailbox, first = self.hub.subscribe(subject)
        if not first:
            self.logger.debug("Joined %s, already followed on NATS.", subject)
            return mailbox
        try:
            await self.feed.subscribe(subject, self.deliver)
        except SEMissionFeedError:
            self.hub.unsubscribe(subject, mailbox)
            self.logger.error("Could not follow %s, the client was not added.", subject)
            raise
        self.logger.info("Following %s on NATS.", subject)
        return mailbox

    async def leave(self, operator_id: UUID, subscription: LiveSubscription, mailbox: LiveMailbox) -> None:
        """Remove a client's mailbox, and stop following the subject when it was the last one.

        Args:
            operator_id (UUID): The Operator of the connection.
            subscription (LiveSubscription): What the client had asked.
            mailbox (LiveMailbox): The mailbox given by ``join``.
        """
        subject = self._subject(operator_id, subscription)
        last = self.hub.unsubscribe(subject, mailbox)
        if not last:
            self.logger.debug("Left %s, other clients remain.", subject)
            return
        await self.feed.unsubscribe(subject)
        self.logger.info("Stopped following %s on NATS.", subject)
