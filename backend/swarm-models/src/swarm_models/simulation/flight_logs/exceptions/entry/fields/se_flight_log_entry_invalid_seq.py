from __future__ import annotations

# First-party imports
from swarm_models.simulation.flight_logs.exceptions.entry.se_invalid_flight_log_entry_exception import (
    SEInvalidFlightLogEntryException,
)


class SEFlightLogEntryInvalidSeq(SEInvalidFlightLogEntryException):
    """Exception raised when an invalid ``seq`` is provided."""
