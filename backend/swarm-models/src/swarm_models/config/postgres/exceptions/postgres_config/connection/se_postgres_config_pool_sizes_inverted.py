from __future__ import annotations

# First-party imports
from swarm_models.config.postgres.exceptions.postgres_config.se_invalid_postgres_config_exception import (
    SEInvalidPostgresConfigException,
)


class SEPostgresConfigPoolSizesInverted(SEInvalidPostgresConfigException):
    """Exception raised when ``pool_min_size`` is greater than ``pool_max_size``."""
