from __future__ import annotations

# First-party imports
from swarm_models.config.simulator.exceptions.simulator_config.s_e_invalid_simulator_config_exception import (
    SEInvalidSimulatorConfigException,
)


class SESimulatorConfigInvalidFlightLogPath(SEInvalidSimulatorConfigException):
    """Exception raised when an invalid ``flight_log_path`` is provided."""
