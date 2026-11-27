from __future__ import annotations

# First-party imports
from swarm_web.models.config.exceptions.signals.se_invalid_signals_config_exception import (
    SEInvalidSignalsConfigException,
)


class SESignalsConfigInvalidMetricsInterval(SEInvalidSignalsConfigException):
    """Exception raised when an invalid ``metrics_interval_s`` is provided."""
