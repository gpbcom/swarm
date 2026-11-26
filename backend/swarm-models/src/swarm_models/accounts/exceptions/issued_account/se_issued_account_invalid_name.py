from __future__ import annotations

# First-party imports
from swarm_models.accounts.exceptions.issued_account.se_invalid_issued_account_exception import (
    SEInvalidIssuedAccountException,
)


class SEIssuedAccountInvalidName(SEInvalidIssuedAccountException):
    """Exception raised when an invalid ``name`` is provided."""
