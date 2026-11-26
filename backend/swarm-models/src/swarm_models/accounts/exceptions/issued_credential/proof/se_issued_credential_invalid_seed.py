from __future__ import annotations

# First-party imports
from swarm_models.accounts.exceptions.issued_credential.se_invalid_issued_credential_exception import (
    SEInvalidIssuedCredentialException,
)


class SEIssuedCredentialInvalidSeed(SEInvalidIssuedCredentialException):
    """Exception raised when an invalid ``seed`` is provided."""
