from __future__ import annotations

# First-party imports
from swarm_models.auth.exceptions.caller.se_invalid_caller_exception import SEInvalidCallerException


class SECallerOperatorMismatch(SEInvalidCallerException):
    """Exception raised when the roles of a Caller do not match its Operator."""
