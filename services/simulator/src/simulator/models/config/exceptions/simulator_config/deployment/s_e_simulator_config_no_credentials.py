from __future__ import annotations

# First-party imports
from simulator.models.config.exceptions.simulator_config.s_e_invalid_simulator_config_exception import (
    SEInvalidSimulatorConfigException,
)


class SESimulatorConfigNoCredentials(SEInvalidSimulatorConfigException):
    """Exception raised when no NATS ``credentials_path`` is provided."""
