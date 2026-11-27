from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Dict, Optional

# Third-party imports
from nats.aio.client import Client
from nats.errors import Error as NatsError
from nats.js.errors import Error as JetStreamError
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

# First-party imports
from swarm_models.events.event import Event
from swarm_models.subjects.operator_subjects import OperatorSubjects
from swarm_nats.models.bus.exceptions import SENatsPublishError
from swarm_nats.models.bus.nats_headers import NatsHeaders
from swarm_nats.tracing.nats_trace_context import NatsTraceContext


class EventPublisher:
    """Publishes the events of an Operator to JetStream.

    Attributes:
        MSG_ID_KEY (ClassVar[str]): The header that deduplicates a message.
        PUBLISH_SPAN (ClassVar[str]): The name of the producer span.
        SUBJECT_ATTRIBUTE (ClassVar[str]): The span attribute that holds the subject.
        connection (Client): The connected NATS client.
        logger (Logger): Logger instance.

    Notes:
        - The identifier of the event is the message identifier, so publishing an event twice stores it once.
        - Each publication runs in a producer span, whose trace context travels in the headers. **The span records the
          subject and never the body.**
        - **A stream must capture the subject**, otherwise the publication is refused.
    """

    MSG_ID_KEY: ClassVar[str] = NatsHeaders.MSG_ID
    PUBLISH_SPAN: ClassVar[str] = "swarm.events.publish"
    SUBJECT_ATTRIBUTE: ClassVar[str] = "messaging.destination.name"

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

    async def publish(self, event: Event) -> int:
        """Publish one event through JetStream.

        Args:
            event (Event): The event.

        Returns:
            int: The sequence of the event in its stream.

        Raises:
            SENatsPublishError: When no stream captures the subject or the publication fails.
        """
        subject = OperatorSubjects(operator_id=event.operator_id).for_event(event)
        with trace.get_tracer(__name__).start_as_current_span(self.PUBLISH_SPAN, kind=SpanKind.PRODUCER) as span:
            span.set_attribute(self.SUBJECT_ATTRIBUTE, subject)
            headers: Dict[str, str] = NatsTraceContext().inject({self.MSG_ID_KEY: str(event.id)})
            try:
                ack = await self.connection.jetstream().publish(
                    subject, event.model_dump_json().encode(), headers=headers
                )
            except (JetStreamError, NatsError) as error:
                span.set_status(Status(StatusCode.ERROR, type(error).__name__))
                self.logger.error("Could not publish event %s: %s.", event.id, type(error).__name__)
                raise SENatsPublishError(
                    f"Invalid event: {str(event.id)!r}. The publication failed with {type(error).__name__}."
                ) from error
        if ack.duplicate:
            self.logger.debug("Event %s was already stored at sequence %d.", event.id, ack.seq)
        else:
            self.logger.info("Published event %s at sequence %d.", event.id, ack.seq)
        return int(ack.seq)
