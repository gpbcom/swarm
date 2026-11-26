from __future__ import annotations

# First-party imports
from swarm_models.storage.exceptions.se_storage_error import SEStorageError


class SEStorageInvalidPageError(SEStorageError):
    """Raised when a page request is not valid."""
