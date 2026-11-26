from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsConnectionError(SENatsError):
    """Raised when a connection to NATS cannot be opened or is lost."""
