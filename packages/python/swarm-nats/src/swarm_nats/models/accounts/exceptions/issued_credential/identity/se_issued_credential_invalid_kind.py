from __future__ import annotations

# First-party imports
from swarm_nats.models.accounts.exceptions.issued_credential.se_invalid_issued_credential_exception import (
    SEInvalidIssuedCredentialException,
)


class SEIssuedCredentialInvalidKind(SEInvalidIssuedCredentialException):
    """Exception raised when an invalid ``kind`` is provided."""
