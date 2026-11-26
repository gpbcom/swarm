from __future__ import annotations

# First-party imports
from swarm_models.simulation.registry.exceptions.simulated_squad_catalog.s_e_invalid_simulated_squad_catalog_exception import (
    SEInvalidSimulatedSquadCatalogException,
)


class SESimulatedSquadCatalogDuplicateDrone(SEInvalidSimulatedSquadCatalogException):
    """Exception raised when two drones share one ``drone_id``."""
