from __future__ import annotations

# First-party imports
from flight_engine.models.telemetry.exceptions.drone_state_catalog.se_invalid_drone_state_catalog_exception import (
    SEInvalidDroneStateCatalogException,
)


class SEDroneStateCatalogInvalidSystemStatusStates(SEInvalidDroneStateCatalogException):
    """Exception raised when an invalid ``system_status_states`` is provided."""
