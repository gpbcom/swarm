from __future__ import annotations

# First-party imports
from gateway.models.auth.exceptions.caller.se_invalid_caller_exception import SEInvalidCallerException


class SECallerInvalidPersonId(SEInvalidCallerException):
    """Exception raised when an invalid ``person_id`` is provided."""
