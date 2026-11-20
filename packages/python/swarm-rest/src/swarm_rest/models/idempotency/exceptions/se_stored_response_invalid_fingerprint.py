from __future__ import annotations

# First-party imports
from swarm_rest.models.idempotency.exceptions.se_invalid_stored_response_exception import (
    SEInvalidStoredResponseException,
)


class SEStoredResponseInvalidFingerprint(SEInvalidStoredResponseException):
    """Exception raised when an invalid ``fingerprint`` is provided."""
