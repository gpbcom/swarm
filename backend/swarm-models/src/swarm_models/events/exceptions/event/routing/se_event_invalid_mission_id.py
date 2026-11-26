from __future__ import annotations

# First-party imports
from swarm_models.models.events.exceptions.event.se_invalid_event_exception import SEInvalidEventException


class SEEventInvalidMissionId(SEInvalidEventException):
    """Exception raised when an invalid ``mission_id`` is provided."""
