from __future__ import annotations

# Standard library imports
from datetime import datetime
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.operators.exceptions import (
    SECellAssignmentInvalidAssignedAt,
    SECellAssignmentInvalidCell,
    SECellAssignmentInvalidOperatorId,
)


class CellAssignment(SwarmModel):
    """The cell an operator belongs to, and since when.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        operator_id (UUID): The version 7 identifier of the operator.
        cell (str): The name of the cell.
        assigned_at (datetime): The moment of the assignment, in UTC.

    Notes:
        - An operator lives in exactly one cell.
        - No field has a default, so ``None`` is refused.
    """

    model_config = ConfigDict(extra="forbid")

    operator_id: UUID = Field(description="The version 7 identifier of the operator.")
    cell: str = Field(description="The name of the cell.")
    assigned_at: datetime = Field(description="The moment of the assignment, in UTC.")

    @field_validator("operator_id", mode="before")
    def validate_operator_id(cls, value: JsonValue) -> UUID:
        """Validate ``operator_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.

        Raises:
            SECellAssignmentInvalidOperatorId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7("operator_id", value, SECellAssignmentInvalidOperatorId)

    @field_validator("cell", mode="before")
    def validate_cell(cls, value: JsonValue) -> str:
        """Validate ``cell``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped name.

        Raises:
            SECellAssignmentInvalidCell: When the value is not a non-empty string.
        """
        return cls.parse_text("cell", value, SECellAssignmentInvalidCell)

    @field_validator("assigned_at", mode="before")
    def validate_assigned_at(cls, value: JsonValue) -> datetime:
        """Validate ``assigned_at``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            datetime: The moment, in UTC.

        Raises:
            SECellAssignmentInvalidAssignedAt: When the value has no time zone or is not a moment.
        """
        return cls.parse_utc("assigned_at", value, SECellAssignmentInvalidAssignedAt)
