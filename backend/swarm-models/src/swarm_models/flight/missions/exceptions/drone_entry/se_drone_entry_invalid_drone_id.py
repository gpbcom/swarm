from __future__ import annotations

# First-party imports
from swarm_models.flight.missions.exceptions.drone_entry.se_invalid_drone_entry_exception import (
    SEInvalidDroneEntryException,
)


class SEDroneEntryInvalidDroneId(SEInvalidDroneEntryException):
    """Exception raised when an invalid ``drone_id`` is provided."""
