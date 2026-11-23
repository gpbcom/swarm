from __future__ import annotations

# First-party imports
from swarm_storage.models.postgres.exceptions.se_storage_error import SEStorageError


class SEStorageOperatorRefusedError(SEStorageError):
    """Raised when the operator is refused by the database."""
