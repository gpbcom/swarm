from __future__ import annotations

# First-party imports
from swarm_models.simulation.flights.exceptions.errors.se_drone_flight_error import (
    SEDroneFlightError,
)


class SEDroneFlightRefusedError(SEDroneFlightError):
    """Raised when a Drone refuses a command."""
