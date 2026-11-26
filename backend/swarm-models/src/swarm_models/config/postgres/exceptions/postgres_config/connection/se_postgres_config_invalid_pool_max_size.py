from __future__ import annotations

# First-party imports
from swarm_models.config.postgres.exceptions.postgres_config.se_invalid_postgres_config_exception import (
    SEInvalidPostgresConfigException,
)


class SEPostgresConfigInvalidPoolMaxSize(SEInvalidPostgresConfigException):
    """Exception raised when an invalid ``pool_max_size`` is provided."""
