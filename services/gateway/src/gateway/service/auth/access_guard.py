from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import List, Optional
from uuid import UUID

# First-party imports
from gateway.models.access.exceptions import SEAccessMissingRoleError, SEAccessWrongOperatorError
from gateway.models.auth.caller import Caller
from swarm_models.models.people.enums import RoleName


class AccessGuard:
    """Checks the Operator and the role of a call.

    Attributes:
        logger (Logger): Logger instance.

    Notes:
        - **The Operator is checked before the role**: a call to another Operator's data is answered as not found,
          whatever the role, so that a caller never learns which roles the data would have needed (BR-008).
        - **The logs never carry the identifiers of the person or of the Operator.**
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Prepare a guard.

        Args:
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def check(self, caller: Caller, roles: List[RoleName], operator_id: Optional[UUID]) -> None:
        """Check that a call targets the caller's Operator and that the caller holds one of the roles.

        Args:
            caller (Caller): The verified person behind the call.
            roles (List[RoleName]): The roles that may make the call, an empty list refuses everyone.
            operator_id (Optional[UUID]): The Operator the call names, none when it names no Operator.

        Raises:
            SEAccessWrongOperatorError: If the call names an Operator other than the caller's.
            SEAccessMissingRoleError: If the caller holds none of the roles.
        """
        if operator_id is None:
            self.logger.debug("The call names no Operator, so only the role is checked.")
        elif operator_id != caller.operator_id:
            self.logger.error("The call names an Operator other than the caller's.")
            raise SEAccessWrongOperatorError("The call names an Operator other than the caller's.")
        else:
            self.logger.debug("The call names the caller's Operator.")
        if set(caller.roles) & set(roles):
            self.logger.debug("The caller holds one of the %d roles the call needs.", len(roles))
        else:
            self.logger.error("The caller holds none of the %d roles the call needs.", len(roles))
            raise SEAccessMissingRoleError("The caller holds none of the roles the call needs.")
