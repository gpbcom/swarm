from __future__ import annotations

# First-party imports
from swarm_models.accounts.exceptions.issued_operator.se_invalid_issued_operator_exception import (
    SEInvalidIssuedOperatorException,
)


class SEIssuedOperatorInvalidPublicKey(SEInvalidIssuedOperatorException):
    """Exception raised when an invalid ``public_key`` is provided."""
