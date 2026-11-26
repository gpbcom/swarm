from __future__ import annotations

# First-party imports
from gateway.models.auth.exceptions.caller.se_invalid_caller_exception import SEInvalidCallerException


class SECallerInvalidOperatorId(SEInvalidCallerException):
    """Exception raised when an invalid ``operator_id`` is provided."""
