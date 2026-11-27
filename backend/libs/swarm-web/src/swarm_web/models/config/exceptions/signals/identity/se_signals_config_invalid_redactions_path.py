from __future__ import annotations

# First-party imports
from swarm_web.models.config.exceptions.signals.se_invalid_signals_config_exception import (
    SEInvalidSignalsConfigException,
)


class SESignalsConfigInvalidRedactionsPath(SEInvalidSignalsConfigException):
    """Exception raised when an invalid ``redactions_path`` is provided."""
