from __future__ import annotations

# First-party imports
from simulator.models.registry.exceptions.simulated_squad_catalog.s_e_invalid_simulated_squad_catalog_exception import (
    SEInvalidSimulatedSquadCatalogException,
)


class SESimulatedSquadCatalogDuplicateEndpoint(SEInvalidSimulatedSquadCatalogException):
    """Exception raised when two drones share one host and port."""
