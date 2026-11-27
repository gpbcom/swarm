from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.created.se_invalid_operator_created_exception import (
    SEInvalidOperatorCreatedException,
)


class SEOperatorCreatedForeignCellAssignment(SEInvalidOperatorCreatedException):
    """Exception raised when the ``cell_assignment`` belongs to another Operator."""
