from __future__ import annotations

# First-party imports
from simulator.models.registry.exceptions.registered_drone.s_e_invalid_registered_drone_exception import (
    SEInvalidRegisteredDroneException,
)


class SERegisteredDroneInvalidSystemId(SEInvalidRegisteredDroneException):
    """Exception raised when an invalid ``system_id`` is provided."""
