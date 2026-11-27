from __future__ import annotations

# First-party imports
from swarm_models.storage.exceptions.se_storage_error import SEStorageError


class SEStorageDuplicateError(SEStorageError):
    """Raised when a row breaks a unique constraint."""
