from __future__ import annotations

# First-party imports
from fleet.models.config.exceptions.se_invalid_fleet_config_exception import SEInvalidFleetConfigException


class SEFleetConfigInvalidSchemaName(SEInvalidFleetConfigException):
    """Exception raised when an invalid ``schema_name`` is provided."""
