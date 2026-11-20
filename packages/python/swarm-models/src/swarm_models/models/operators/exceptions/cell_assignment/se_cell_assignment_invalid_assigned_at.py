from __future__ import annotations

# First-party imports
from swarm_models.models.operators.exceptions.cell_assignment.se_invalid_cell_assignment_exception import (
    SEInvalidCellAssignmentException,
)


class SECellAssignmentInvalidAssignedAt(SEInvalidCellAssignmentException):
    """Exception raised when an invalid ``assigned_at`` is provided."""
