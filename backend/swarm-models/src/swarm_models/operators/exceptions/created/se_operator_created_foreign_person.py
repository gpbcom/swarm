from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.created.se_invalid_operator_created_exception import (
    SEInvalidOperatorCreatedException,
)


class SEOperatorCreatedForeignPerson(SEInvalidOperatorCreatedException):
    """Exception raised when the ``first_mission_planner`` does not belong to the Operator."""
