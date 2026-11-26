from __future__ import annotations

# First-party imports
from simulator.models.flight_logs.exceptions.store.se_flight_log_store_error import (
    SEFlightLogStoreError,
)


class SEFlightLogStoreUnwritableError(SEFlightLogStoreError):
    """Raised when the Flight log cannot be written."""
