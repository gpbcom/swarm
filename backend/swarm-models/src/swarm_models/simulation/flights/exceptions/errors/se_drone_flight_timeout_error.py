from __future__ import annotations

# First-party imports
from swarm_models.simulation.flights.exceptions.errors.se_drone_flight_error import (
    SEDroneFlightError,
)


class SEDroneFlightTimeoutError(SEDroneFlightError):
    """Raised when a Drone does not answer within its deadline."""
