from __future__ import annotations

# First-party imports
from swarm_models.flight.missions.exceptions.mission_entry.se_invalid_mission_entry_exception import (
    SEInvalidMissionEntryException,
)


class SEMissionEntryInvalidOperatorId(SEInvalidMissionEntryException):
    """Exception raised when an invalid ``operator_id`` is provided."""
