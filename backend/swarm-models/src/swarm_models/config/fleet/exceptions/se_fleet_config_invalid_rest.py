from __future__ import annotations

# First-party imports
from swarm_models.config.fleet.exceptions.se_invalid_fleet_config_exception import SEInvalidFleetConfigException


class SEFleetConfigInvalidRest(SEInvalidFleetConfigException):
    """Exception raised when an invalid ``rest`` is provided."""
