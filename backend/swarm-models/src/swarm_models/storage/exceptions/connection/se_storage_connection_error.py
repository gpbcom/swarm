from __future__ import annotations

# First-party imports
from swarm_models.storage.exceptions.se_storage_error import SEStorageError


class SEStorageConnectionError(SEStorageError):
    """Raised when the database cannot be reached."""
