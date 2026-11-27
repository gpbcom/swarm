from __future__ import annotations

# First-party imports
from swarm_models.config.gateway.exceptions.operator_directory.se_invalid_operator_directory_config_exception import (
    SEInvalidOperatorDirectoryConfigException,
)


class SEOperatorDirectoryConfigInvalidCell(SEInvalidOperatorDirectoryConfigException):
    """Exception raised when an invalid ``cell`` is provided."""
