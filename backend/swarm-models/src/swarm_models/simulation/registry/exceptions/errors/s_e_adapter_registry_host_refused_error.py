from __future__ import annotations

# First-party imports
from simulator.models.registry.exceptions.errors.s_e_adapter_registry_error import (
    SEAdapterRegistryError,
)


class SEAdapterRegistryHostRefusedError(SEAdapterRegistryError):
    """Raised when a host is not a simulated one."""
