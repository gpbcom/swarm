from __future__ import annotations

# First-party imports
from flight_engine.models.clients.exceptions.se_flight_engine_client_error import SEFlightEngineClientError


class SESquadFramePublishError(SEFlightEngineClientError):
    """Raised when a SquadFrame cannot be published to the leaf node."""
