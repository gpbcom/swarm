from __future__ import annotations

# First-party imports
from swarm_models.storage.exceptions.se_storage_error import SEStorageError


class SEStorageNotOpenError(SEStorageError):
    """Raised when the storage is used before it is opened."""
