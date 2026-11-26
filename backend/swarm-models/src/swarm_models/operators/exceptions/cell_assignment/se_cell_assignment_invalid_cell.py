from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.cell_assignment.se_invalid_cell_assignment_exception import (
    SEInvalidCellAssignmentException,
)


class SECellAssignmentInvalidCell(SEInvalidCellAssignmentException):
    """Exception raised when an invalid ``cell`` is provided."""
