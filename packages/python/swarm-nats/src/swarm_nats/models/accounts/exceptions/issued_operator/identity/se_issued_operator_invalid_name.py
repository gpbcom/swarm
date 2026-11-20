from __future__ import annotations

from swarm_nats.models.accounts.exceptions.issued_operator.se_invalid_issued_operator_exception import (
    SEInvalidIssuedOperatorException,
)


class SEIssuedOperatorInvalidName(SEInvalidIssuedOperatorException):
    """Exception raised when an invalid ``name`` is provided."""
