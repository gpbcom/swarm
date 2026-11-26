from __future__ import annotations

# First-party imports
from flight_engine.models.missions.exceptions.mission_entry.se_invalid_mission_entry_exception import (
    SEInvalidMissionEntryException,
)


class SEMissionEntryInvalidMavlinkPort(SEInvalidMissionEntryException):
    """Exception raised when an invalid ``mavlink_port`` is provided."""
