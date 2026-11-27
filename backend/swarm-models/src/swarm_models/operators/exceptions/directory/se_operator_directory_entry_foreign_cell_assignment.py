from __future__ import annotations

# First-party imports
from swarm_models.operators.exceptions.directory.se_invalid_operator_directory_entry_exception import (
    SEInvalidOperatorDirectoryEntryException,
)


class SEOperatorDirectoryEntryForeignCellAssignment(SEInvalidOperatorDirectoryEntryException):
    """Exception raised when the ``cell_assignment`` belongs to another Operator."""
