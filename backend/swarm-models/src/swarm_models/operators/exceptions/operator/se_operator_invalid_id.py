from __future__ import annotations

# First-party imports
from swarm_models.models.operators.exceptions.operator.se_invalid_operator_exception import SEInvalidOperatorException


class SEOperatorInvalidId(SEInvalidOperatorException):
    """Exception raised when an invalid ``id`` is provided."""
