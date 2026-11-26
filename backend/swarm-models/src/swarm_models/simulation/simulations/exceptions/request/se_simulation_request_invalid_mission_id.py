from __future__ import annotations

# First-party imports
from swarm_models.simulation.simulations.exceptions.request.se_invalid_simulation_request_exception import (
    SEInvalidSimulationRequestException,
)


class SESimulationRequestInvalidMissionId(SEInvalidSimulationRequestException):
    """Exception raised when an invalid ``mission_id`` is provided."""
