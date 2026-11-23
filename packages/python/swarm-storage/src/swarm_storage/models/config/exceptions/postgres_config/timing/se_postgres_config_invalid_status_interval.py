from __future__ import annotations

# First-party imports
from swarm_storage.models.config.exceptions.postgres_config.se_invalid_postgres_config_exception import (
    SEInvalidPostgresConfigException,
)


class SEPostgresConfigInvalidStatusInterval(SEInvalidPostgresConfigException):
    """Exception raised when an invalid ``status_interval_s`` is provided."""
