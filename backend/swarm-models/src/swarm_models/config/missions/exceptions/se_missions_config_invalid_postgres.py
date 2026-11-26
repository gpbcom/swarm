from __future__ import annotations

# First-party imports
from swarm_models.config.missions.exceptions.se_invalid_missions_config_exception import (
    SEInvalidMissionsConfigException,
)


class SEMissionsConfigInvalidPostgres(SEInvalidMissionsConfigException):
    """Exception raised when an invalid ``postgres`` is provided."""
