from __future__ import annotations

# Standard library imports
from typing import Optional
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.people.enums import RoleName
from swarm_models.models.people.exceptions import (
    SERoleInvalidName,
    SERoleInvalidOperatorId,
    SERoleInvalidPersonId,
    SERoleOperatorMismatch,
)


class Role(SwarmModel):
    """A role held by a person.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        person_id (UUID): The version 7 identifier of the person.
        operator_id (Optional[UUID]): The Operator the role applies to, ``None`` for a Swarm administrator.
        name (RoleName): The role.

    Notes:
        **``operator_id`` is ``None`` exactly for ``RoleName.SWARM_ADMINISTRATOR``**, because a Swarm administrator
        has no access to the data of Operators.
    """

    model_config = ConfigDict(extra="forbid")

    person_id: UUID = Field(description="The version 7 identifier of the person.")
    operator_id: Optional[UUID] = Field(default=None, description="The Operator the role applies to, if any.")
    name: RoleName = Field(description="The role.")

    @field_validator("person_id", mode="before")
    def validate_person_id(cls, value: JsonValue) -> UUID:
        """Validate ``person_id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.
        """
        return cls.parse_uuid7("person_id", value, SERoleInvalidPersonId)

    @field_validator("operator_id", mode="before")
    def validate_operator_id(cls, value: JsonValue) -> Optional[UUID]:
        """Validate ``operator_id``, where ``None`` becomes the default.

        Args:
            value (JsonValue): The raw value.

        Returns:
            Optional[UUID]: The version 7 UUID, or ``None``.
        """
        if value is None:
            return None
        return cls.parse_uuid7("operator_id", value, SERoleInvalidOperatorId)

    @field_validator("name", mode="before")
    def validate_name(cls, value: JsonValue) -> RoleName:
        """Validate ``name``.

        Args:
            value (JsonValue): A role or its string form.

        Returns:
            RoleName: The role.

        Raises:
            SERoleInvalidName: When the value is not one of the roles.
        """
        members = [member.value for member in RoleName]
        if isinstance(value, str) and value in members:
            return RoleName(value)
        raise SERoleInvalidName(f"Invalid name: {value!r}. Must be one of {members}.")

    @model_validator(mode="after")
    def validate_operator_matches_name(self) -> Role:
        """Check that ``operator_id`` is ``None`` exactly for a Swarm administrator.

        Returns:
            Role: The validated role.

        Raises:
            SERoleOperatorMismatch: When the operator and the role disagree.
        """
        administrator = self.name is RoleName.SWARM_ADMINISTRATOR
        if administrator != (self.operator_id is None):
            raise SERoleOperatorMismatch(
                f"Invalid operator_id: {self.operator_id!r} for role {self.name.value!r}. "
                "Must be None exactly for a Swarm administrator."
            )
        return self
