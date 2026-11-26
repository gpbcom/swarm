from __future__ import annotations

# First-party imports
from swarm_nats.models.accounts.exceptions.issued_operator.se_invalid_issued_operator_exception import (
    SEInvalidIssuedOperatorException,
)


class SEIssuedOperatorInvalidSeed(SEInvalidIssuedOperatorException):
    """Exception raised when an invalid ``seed`` is provided."""
