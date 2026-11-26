from __future__ import annotations

# First-party imports
from flight_engine.models.missions.exceptions.drone_entry.se_invalid_drone_entry_exception import (
    SEInvalidDroneEntryException,
)


class SEDroneEntryInvalidSystemId(SEInvalidDroneEntryException):
    """Exception raised when an invalid ``system_id`` is provided."""
