from __future__ import annotations

# Third-party imports
from pydantic import ConfigDict, Field, model_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_models.operators.exceptions import (
    SEOperatorCreatedForeignCellAssignment,
    SEOperatorCreatedForeignPerson,
)
from swarm_models.operators.operator import Operator
from swarm_models.people.person import Person


class OperatorCreated(SwarmModel):
    """What the creation of an Operator answers: the Operator, its cell and its first Mission planner.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        operator (Operator): The new Operator.
        cell_assignment (CellAssignment): The cell the Operator lives in.
        first_mission_planner (Person): The first Mission planner, who belongs to the Operator.

    Notes:
        The cell assignment and the person must belong to the Operator.
    """

    model_config = ConfigDict(extra="forbid")

    operator: Operator = Field(description="The new Operator.")
    cell_assignment: CellAssignment = Field(description="The cell the Operator lives in.")
    first_mission_planner: Person = Field(description="The first Mission planner of the Operator.")

    @model_validator(mode="after")
    def validate_belonging(self) -> OperatorCreated:
        """Check that the cell assignment and the person are the Operator's.

        Returns:
            OperatorCreated: The answer itself.

        Raises:
            SEOperatorCreatedForeignCellAssignment: When the assignment names another Operator.
            SEOperatorCreatedForeignPerson: When the person belongs to no Operator or to another one.
        """
        if self.cell_assignment.operator_id != self.operator.id:
            raise SEOperatorCreatedForeignCellAssignment(
                f"Invalid cell_assignment: {self.cell_assignment.operator_id}. Must belong to {self.operator.id}."
            )
        if self.first_mission_planner.operator_id != self.operator.id:
            raise SEOperatorCreatedForeignPerson(
                f"Invalid first_mission_planner: {self.first_mission_planner.operator_id}. "
                f"Must belong to {self.operator.id}."
            )
        return self
