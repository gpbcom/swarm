from __future__ import annotations

# First-party imports
from swarm_models.simulation.simulations.exceptions.accepted.se_invalid_simulation_accepted_exception import (
    SEInvalidSimulationAcceptedException,
)


class SESimulationAcceptedInvalidDroneIds(SEInvalidSimulationAcceptedException):
    """Exception raised when an invalid ``drone_ids`` is provided."""
