from __future__ import annotations

# First-party imports
from swarm_storage.models.config.exceptions.postgres_config.se_invalid_postgres_config_exception import (
    SEInvalidPostgresConfigException,
)


class SEPostgresConfigInvalidCommandTimeout(SEInvalidPostgresConfigException):
    """Exception raised when an invalid ``command_timeout_s`` is provided."""
