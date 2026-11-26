from __future__ import annotations

# First-party imports
from swarm_models.models.people.exceptions.role.se_invalid_role_exception import SEInvalidRoleException


class SERoleOperatorMismatch(SEInvalidRoleException):
    """Exception raised when ``operator_id`` does not match the role ``name``."""
