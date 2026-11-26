from __future__ import annotations

# First-party imports
from swarm_models.simulation.simulations.exceptions.accepted.se_invalid_simulation_accepted_exception import (
    SEInvalidSimulationAcceptedException,
)


class SESimulationAcceptedInvalidMissionId(SEInvalidSimulationAcceptedException):
    """Exception raised when an invalid ``mission_id`` is provided."""
