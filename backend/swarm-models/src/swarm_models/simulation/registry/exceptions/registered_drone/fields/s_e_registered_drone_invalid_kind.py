from __future__ import annotations

# First-party imports
from swarm_models.simulation.registry.exceptions.registered_drone.s_e_invalid_registered_drone_exception import (
    SEInvalidRegisteredDroneException,
)


class SERegisteredDroneInvalidKind(SEInvalidRegisteredDroneException):
    """Exception raised when an invalid ``kind`` is provided."""
