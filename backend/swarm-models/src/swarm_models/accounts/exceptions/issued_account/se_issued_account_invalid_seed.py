from __future__ import annotations

# First-party imports
from swarm_nats.models.accounts.exceptions.issued_account.se_invalid_issued_account_exception import (
    SEInvalidIssuedAccountException,
)


class SEIssuedAccountInvalidSeed(SEInvalidIssuedAccountException):
    """Exception raised when an invalid ``seed`` is provided."""
