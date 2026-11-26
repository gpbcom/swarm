from __future__ import annotations

# First-party imports
from simulator.models.config.exceptions.registry_config.s_e_invalid_registry_config_exception import (
    SEInvalidRegistryConfigException,
)


class SERegistryConfigInvalidSimulatedHosts(SEInvalidRegistryConfigException):
    """Exception raised when an invalid ``simulated_hosts`` is provided."""
