from __future__ import annotations

# First-party imports
from swarm_storage.models.postgres.exceptions.se_storage_error import SEStorageError


class SEStorageDsnMissingError(SEStorageError):
    """Raised when the DSN environment entry is missing or empty."""
