from __future__ import annotations

# First-party imports
from swarm_models.rest.idempotency.exceptions.se_invalid_stored_response_exception import (
    SEInvalidStoredResponseException,
)


class SEStoredResponseInvalidHeaders(SEInvalidStoredResponseException):
    """Exception raised when an invalid ``headers`` is provided."""
