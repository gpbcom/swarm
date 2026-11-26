from __future__ import annotations

# First-party imports
from swarm_nats.models.bus.exceptions.se_nats_error import SENatsError


class SENatsAccountPushRefusedError(SENatsError):
    """Raised when the NATS server refuses the push of an account."""
