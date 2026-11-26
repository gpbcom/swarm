from __future__ import annotations

# First-party imports
from swarm_models.storage.exceptions.se_storage_error import SEStorageError


class SEStorageVersionConflictError(SEStorageError):
    """Raised when a row was changed by another writer."""
