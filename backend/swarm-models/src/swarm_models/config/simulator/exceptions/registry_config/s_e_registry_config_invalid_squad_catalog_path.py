from __future__ import annotations

# First-party imports
from swarm_models.config.simulator.exceptions.registry_config.s_e_invalid_registry_config_exception import (
    SEInvalidRegistryConfigException,
)


class SERegistryConfigInvalidSquadCatalogPath(SEInvalidRegistryConfigException):
    """Exception raised when an invalid ``squad_catalog_path`` is provided."""
