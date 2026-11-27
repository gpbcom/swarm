from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, Optional, Tuple

# Third-party imports
from opentelemetry import baggage
from opentelemetry.context import Context
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor

# First-party imports
from swarm_web.models.enums import SignalAttribute


class MissionSpanProcessor(SpanProcessor):
    """Copies the Operator and the Mission of the baggage onto every span that starts.

    Attributes:
        KEYS (ClassVar[Tuple[SignalAttribute, ...]]): The baggage entries carried onto the span.
        logger (Logger): Logger instance.

    Notes:
        - One process serves several Operators and Missions, so these resource-like attributes are carried by each
          span rather than by the process resource.
        - A span with no such baggage entry gets no such attribute.
    """

    KEYS: ClassVar[Tuple[SignalAttribute, ...]] = (SignalAttribute.OPERATOR_ID, SignalAttribute.MISSION_ID)

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the processor.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def on_start(self, span: Span, parent_context: Optional[Context] = None) -> None:
        """Copy the baggage entries of the parent context onto the span.

        Args:
            span (Span): The span that starts.
            parent_context (Optional[Context]): The context the span starts in.
        """
        for key in self.KEYS:
            value = baggage.get_baggage(key.value, parent_context)
            if value is None:
                self.logger.debug("No %s in the baggage.", key.value)
            else:
                span.set_attribute(key.value, str(value))
                self.logger.debug("Carried %s onto the span.", key.value)

    def on_end(self, span: ReadableSpan) -> None:
        """Do nothing when a span ends.

        Args:
            span (ReadableSpan): The span that ended.
        """
        self.logger.debug("A span ended.")

    def shutdown(self) -> None:
        """Do nothing, the processor holds nothing."""
        self.logger.debug("Shut the processor down.")

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Report that nothing is waiting to be flushed.

        Args:
            timeout_millis (int): The time allowed, ignored.

        Returns:
            bool: Always True.
        """
        self.logger.debug("Nothing to flush.")
        return True
