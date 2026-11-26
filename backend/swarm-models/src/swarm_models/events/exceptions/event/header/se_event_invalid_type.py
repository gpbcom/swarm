from __future__ import annotations

# First-party imports
from swarm_models.events.exceptions.event.se_invalid_event_exception import SEInvalidEventException


class SEEventInvalidType(SEInvalidEventException):
    """Exception raised when an invalid ``type`` is provided."""
