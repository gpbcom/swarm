from __future__ import annotations

# First-party imports
from swarm_storage.models.config.exceptions.postgres_config.se_invalid_postgres_config_exception import (
    SEInvalidPostgresConfigException,
)


class SEPostgresConfigInvalidDsnKey(SEInvalidPostgresConfigException):
    """Exception raised when an invalid ``dsn_key`` is provided."""
