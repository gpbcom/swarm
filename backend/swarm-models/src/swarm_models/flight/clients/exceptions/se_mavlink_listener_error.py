from __future__ import annotations

# First-party imports
from flight_engine.models.clients.exceptions.se_flight_engine_client_error import SEFlightEngineClientError


class SEMavlinkListenerError(SEFlightEngineClientError):
    """Raised when the MAVLink listener cannot bind its UDP port."""
