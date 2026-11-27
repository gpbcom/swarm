from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.operator.se_invalid_operator_exception import SEInvalidOperatorException


class SEOperatorInvalidAnchoring(SEInvalidOperatorException):
    """Exception raised when an invalid ``anchoring`` is provided."""
