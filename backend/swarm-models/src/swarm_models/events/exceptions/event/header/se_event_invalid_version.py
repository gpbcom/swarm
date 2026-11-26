from __future__ import annotations

# First-party imports
from swarm_models.models.events.exceptions.event.se_invalid_event_exception import SEInvalidEventException


class SEEventInvalidVersion(SEInvalidEventException):
    """Exception raised when an invalid ``version`` is provided."""
