from __future__ import annotations

# Third-party imports
from pydantic import ConfigDict, Field, model_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_models.operators.exceptions import SEOperatorDirectoryEntryForeignCellAssignment
from swarm_models.operators.operator import Operator


class OperatorDirectoryEntry(SwarmModel):
    """An Operator with its cell, as the directory of the gateway holds it.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        operator (Operator): The Operator.
        cell_assignment (CellAssignment): The cell the Operator lives in.

    Notes:
        The cell assignment must be the Operator's own.
    """

    model_config = ConfigDict(extra="forbid")

    operator: Operator = Field(description="The Operator.")
    cell_assignment: CellAssignment = Field(description="The cell the Operator lives in.")

    @model_validator(mode="after")
    def validate_belonging(self) -> OperatorDirectoryEntry:
        """Check that the cell assignment is the Operator's.

        Returns:
            OperatorDirectoryEntry: The entry itself.

        Raises:
            SEOperatorDirectoryEntryForeignCellAssignment: When the assignment names another Operator.
        """
        if self.cell_assignment.operator_id != self.operator.id:
            raise SEOperatorDirectoryEntryForeignCellAssignment(
                f"Invalid cell_assignment: {self.cell_assignment.operator_id}. Must belong to {self.operator.id}."
            )
        return self
