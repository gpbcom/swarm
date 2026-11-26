from __future__ import annotations

# First-party imports
from missions.models.config.exceptions.se_invalid_missions_config_exception import (
    SEInvalidMissionsConfigException,
)


class SEMissionsConfigInvalidSchemaName(SEInvalidMissionsConfigException):
    """Exception raised when an invalid ``schema_name`` is provided."""
