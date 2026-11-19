from __future__ import annotations

# Standard library imports
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.operators.exceptions import SEOperatorInvalidId, SEOperatorInvalidName


class Operator(SwarmModel):
    """A person who pilots drones, global to every cell.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        id (UUID): The version 7 identifier of the operator.
        name (str): The name of the operator.

    Notes:
        - An operator lives in exactly one cell, given by its ``CellAssignment``.
        - No field has a default, so ``None`` is refused.
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(description="The version 7 identifier of the operator.")
    name: str = Field(description="The name of the operator.")

    @field_validator("id", mode="before")
    def validate_id(cls, value: JsonValue) -> UUID:
        """Validate ``id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.

        Raises:
            SEOperatorInvalidId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7("id", value, SEOperatorInvalidId)

    @field_validator("name", mode="before")
    def validate_name(cls, value: JsonValue) -> str:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped name.

        Raises:
            SEOperatorInvalidName: When the value is not a non-empty string.
        """
        return cls.parse_text("name", value, SEOperatorInvalidName)
