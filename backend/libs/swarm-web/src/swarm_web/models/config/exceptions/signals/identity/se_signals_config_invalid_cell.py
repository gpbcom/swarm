from __future__ import annotations

# First-party imports
from swarm_web.models.config.exceptions.signals.se_invalid_signals_config_exception import (
    SEInvalidSignalsConfigException,
)


class SESignalsConfigInvalidCell(SEInvalidSignalsConfigException):
    """Exception raised when an invalid ``cell`` is provided."""
