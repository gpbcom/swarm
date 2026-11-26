from __future__ import annotations

# First-party imports
from swarm_models.auth.exceptions.caller.se_invalid_caller_exception import SEInvalidCallerException


class SECallerInvalidRoles(SEInvalidCallerException):
    """Exception raised when an invalid ``roles`` is provided."""
