from __future__ import annotations

# First-party imports
from simulator.models.flight_logs.exceptions.store.se_flight_log_store_error import (
    SEFlightLogStoreError,
)


class SEFlightLogStoreNotSimulatedError(SEFlightLogStoreError):
    """Raised when a Flight log entry that is not simulated is offered to the store."""
