from __future__ import annotations

# First-party imports
from simulator.models.mavlink.exceptions.se_mavlink_client_error import SEMavlinkClientError


class SEMavlinkClientRefusedError(SEMavlinkClientError):
    """Raised when a Drone refuses a mission or a command."""
