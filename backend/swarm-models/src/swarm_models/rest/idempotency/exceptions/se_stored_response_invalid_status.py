from __future__ import annotations

# First-party imports
from swarm_models.rest.idempotency.exceptions.se_invalid_stored_response_exception import (
    SEInvalidStoredResponseException,
)


class SEStoredResponseInvalidStatus(SEInvalidStoredResponseException):
    """Exception raised when an invalid ``status`` is provided."""
