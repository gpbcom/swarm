from __future__ import annotations

# First-party imports
from swarm_models.simulation.registry.exceptions.errors.s_e_adapter_registry_error import (
    SEAdapterRegistryError,
)


class SEAdapterRegistryUnknownDroneError(SEAdapterRegistryError):
    """Raised when a Drone is not in the adapter registry."""
