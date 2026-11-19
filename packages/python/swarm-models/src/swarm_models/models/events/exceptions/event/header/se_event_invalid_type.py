from __future__ import annotations

from swarm_models.models.events.exceptions.event.se_invalid_event_exception import SEInvalidEventException


class SEEventInvalidType(SEInvalidEventException):
    """Exception raised when an invalid ``type`` is provided."""
