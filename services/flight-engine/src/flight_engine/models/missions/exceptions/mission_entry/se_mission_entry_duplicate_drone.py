from __future__ import annotations

# First-party imports
from flight_engine.models.missions.exceptions.mission_entry.se_invalid_mission_entry_exception import (
    SEInvalidMissionEntryException,
)


class SEMissionEntryDuplicateDrone(SEInvalidMissionEntryException):
    """Raised when two Drones of a Mission have the same ``drone_id``."""
