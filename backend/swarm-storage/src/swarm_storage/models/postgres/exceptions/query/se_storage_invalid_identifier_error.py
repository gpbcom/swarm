from __future__ import annotations

# First-party imports
from swarm_storage.models.postgres.exceptions.se_storage_error import SEStorageError


class SEStorageInvalidIdentifierError(SEStorageError):
    """Raised when an identifier is not valid."""
