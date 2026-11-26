from __future__ import annotations

# First-party imports
from swarm_models.schemas.exceptions.se_schema_error import SESchemaError


class SESchemaUnwritableError(SESchemaError):
    """Raised when a schema file cannot be written."""
