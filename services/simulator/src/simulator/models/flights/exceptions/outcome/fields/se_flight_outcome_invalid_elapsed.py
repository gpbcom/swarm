from __future__ import annotations

# First-party imports
from simulator.models.flights.exceptions.outcome.se_invalid_flight_outcome_exception import (
    SEInvalidFlightOutcomeException,
)


class SEFlightOutcomeInvalidElapsed(SEInvalidFlightOutcomeException):
    """Exception raised when an invalid ``elapsed_s`` is provided."""
