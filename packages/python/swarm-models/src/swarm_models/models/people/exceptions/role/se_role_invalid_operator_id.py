from __future__ import annotations

from swarm_models.models.people.exceptions.role.se_invalid_role_exception import SEInvalidRoleException


class SERoleInvalidOperatorId(SEInvalidRoleException):
    """Exception raised when an invalid ``operator_id`` is provided."""
