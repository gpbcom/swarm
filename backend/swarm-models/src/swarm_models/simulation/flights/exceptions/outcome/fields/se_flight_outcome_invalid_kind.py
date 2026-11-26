from __future__ import annotations

# First-party imports
from swarm_models.simulation.flights.exceptions.outcome.se_invalid_flight_outcome_exception import (
    SEInvalidFlightOutcomeException,
)


class SEFlightOutcomeInvalidKind(SEInvalidFlightOutcomeException):
    """Exception raised when an invalid ``kind`` is provided."""
