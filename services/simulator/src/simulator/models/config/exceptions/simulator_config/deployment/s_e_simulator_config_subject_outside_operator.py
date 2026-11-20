from __future__ import annotations

# First-party imports
from simulator.models.config.exceptions.simulator_config.s_e_invalid_simulator_config_exception import (
    SEInvalidSimulatorConfigException,
)


class SESimulatorConfigSubjectOutsideOperator(SEInvalidSimulatorConfigException):
    """Exception raised when the responder ``subject`` is outside the operator."""
