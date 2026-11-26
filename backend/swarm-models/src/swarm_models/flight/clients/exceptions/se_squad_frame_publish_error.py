from __future__ import annotations

# First-party imports
from swarm_models.flight.clients.exceptions.se_flight_engine_client_error import SEFlightEngineClientError


class SESquadFramePublishError(SEFlightEngineClientError):
    """Raised when a SquadFrame cannot be published to the leaf node."""
