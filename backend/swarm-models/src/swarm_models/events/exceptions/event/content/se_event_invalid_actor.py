from __future__ import annotations

# First-party imports
from swarm_models.events.exceptions.event.se_invalid_event_exception import SEInvalidEventException


class SEEventInvalidActor(SEInvalidEventException):
    """Exception raised when an invalid ``actor`` is provided."""
