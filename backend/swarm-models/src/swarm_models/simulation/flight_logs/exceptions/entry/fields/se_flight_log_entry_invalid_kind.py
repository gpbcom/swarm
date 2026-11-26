from __future__ import annotations

# First-party imports
from simulator.models.flight_logs.exceptions.entry.se_invalid_flight_log_entry_exception import (
    SEInvalidFlightLogEntryException,
)


class SEFlightLogEntryInvalidKind(SEInvalidFlightLogEntryException):
    """Exception raised when an invalid ``kind`` is provided."""
