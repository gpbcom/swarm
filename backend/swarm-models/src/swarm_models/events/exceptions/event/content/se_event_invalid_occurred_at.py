from __future__ import annotations

# First-party imports
from swarm_models.models.events.exceptions.event.se_invalid_event_exception import SEInvalidEventException


class SEEventInvalidOccurredAt(SEInvalidEventException):
    """Exception raised when an invalid ``occurred_at`` is provided."""
