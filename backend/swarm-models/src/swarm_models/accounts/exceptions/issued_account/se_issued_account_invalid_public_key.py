from __future__ import annotations

# First-party imports
from swarm_models.accounts.exceptions.issued_account.se_invalid_issued_account_exception import (
    SEInvalidIssuedAccountException,
)


class SEIssuedAccountInvalidPublicKey(SEInvalidIssuedAccountException):
    """Exception raised when an invalid ``public_key`` is provided."""
