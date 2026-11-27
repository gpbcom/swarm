from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.operator.se_invalid_operator_exception import SEInvalidOperatorException


class SEOperatorInvalidJurisdictions(SEInvalidOperatorException):
    """Exception raised when an invalid ``jurisdictions`` is provided."""
