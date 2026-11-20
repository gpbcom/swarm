from __future__ import annotations

# First-party imports
from simulator.models.registry.exceptions.errors.s_e_adapter_registry_error import (
    SEAdapterRegistryError,
)


class SEAdapterRegistryDuplicateDroneError(SEAdapterRegistryError):
    """Raised when a Drone is registered twice."""
