from __future__ import annotations

# First-party imports
from simulator.models.flights.exceptions.errors.se_drone_flight_error import (
    SEDroneFlightError,
)


class SEDroneFlightTimeoutError(SEDroneFlightError):
    """Raised when a Drone does not answer within its deadline."""
