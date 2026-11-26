from __future__ import annotations

# First-party imports
from simulator.models.mavlink.exceptions.se_mavlink_client_error import SEMavlinkClientError


class SEMavlinkClientTimeoutError(SEMavlinkClientError):
    """Raised when a Drone does not answer within its deadline."""
