from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional
from uuid import UUID

# Third-party imports
from nats.aio.client import Client
from nats.errors import Error as NatsError

# First-party imports
from swarm_clients.flight.leaf.frame_sink import FrameSink
from swarm_models.enums import LiveTopicKind
from swarm_models.flight.clients.exceptions import SESquadFramePublishError
from swarm_models.subjects.operator_subjects import OperatorSubjects


class SquadFramePublisher(FrameSink):
    """Publishes the SquadFrame of a Mission to the leaf node, on core NATS.

    Attributes:
        connection (Client): The connected NATS client of the leaf node.
        logger (Logger): Logger instance.

    Notes:
        - The subject is ``op.<operator_id>.mission.<mission_id>.squad``, so a subscriber of another Operator never
          sees the frame.
        - A frame is only worth its tick, so it goes out without JetStream and is not stored.
    """

    def __init__(self, connection: Client, logger: Optional[Logger] = None) -> None:
        """Keep the connection.

        Args:
            connection (Client): The connected NATS client.
            logger (Optional[Logger]): Logger instance.
        """
        self.connection = connection
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def publish(self, operator_id: UUID, mission_id: UUID, data: bytes) -> None:
        """Publish one encoded SquadFrame.

        Args:
            operator_id (UUID): The Operator of the Mission.
            mission_id (UUID): The Mission the frame belongs to.
            data (bytes): The MessagePack frame.

        Raises:
            SESquadFramePublishError: When NATS refuses the publication.
        """
        subject = OperatorSubjects(operator_id=operator_id).mission(mission_id, LiveTopicKind.SQUAD)
        try:
            await self.connection.publish(subject, data)
        except NatsError as error:
            self.logger.error("Could not publish a SquadFrame on %s: %s.", subject, type(error).__name__)
            raise SESquadFramePublishError(
                f"Invalid subject: {subject!r}. The publication failed with {type(error).__name__}."
            ) from error
        self.logger.debug("Published %d bytes on %s.", len(data), subject)
