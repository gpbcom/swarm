from __future__ import annotations

# First-party imports
from swarm_models.flight.telemetry.exceptions.drone_state_catalog.se_invalid_drone_state_catalog_exception import (
    SEInvalidDroneStateCatalogException,
)


class SEDroneStateCatalogInvalidDefaultState(SEInvalidDroneStateCatalogException):
    """Exception raised when an invalid ``default_state`` is provided."""
