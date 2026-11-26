from __future__ import annotations

# First-party imports
from swarm_models.people.exceptions.role.se_invalid_role_exception import SEInvalidRoleException


class SERoleInvalidName(SEInvalidRoleException):
    """Exception raised when an invalid ``name`` is provided."""
