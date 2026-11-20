from __future__ import annotations

from swarm_nats.models.accounts.exceptions.issued_credential.se_invalid_issued_credential_exception import (
    SEInvalidIssuedCredentialException,
)


class SEIssuedCredentialInvalidPublicKey(SEInvalidIssuedCredentialException):
    """Exception raised when an invalid ``public_key`` is provided."""
