from __future__ import annotations

from swarm_models.models.operators.exceptions.operator.se_invalid_operator_exception import SEInvalidOperatorException


class SEOperatorInvalidName(SEInvalidOperatorException):
    """Exception raised when an invalid ``name`` is provided."""
