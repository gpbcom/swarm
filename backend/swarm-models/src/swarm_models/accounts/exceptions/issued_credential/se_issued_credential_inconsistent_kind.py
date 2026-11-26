from __future__ import annotations

# First-party imports
from swarm_models.accounts.exceptions.issued_credential.se_invalid_issued_credential_exception import (
    SEInvalidIssuedCredentialException,
)


class SEIssuedCredentialInconsistentKind(SEInvalidIssuedCredentialException):
    """Exception raised when the kind and the operator of a credential are inconsistent."""
