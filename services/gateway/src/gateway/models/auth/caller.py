from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal, Optional, Union
from uuid import UUID

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from gateway.models.auth.exceptions import (
    SECallerInvalidOperatorId,
    SECallerInvalidPersonId,
    SECallerInvalidRoles,
    SECallerOperatorMismatch,
)
from swarm_models.models.people.enums import RoleName


class Caller(BaseModel):
    """The verified person, Operator and roles behind a call.

    Attributes:
        person_id (UUID): The person who calls.
        operator_id (Optional[UUID]): The Operator the person belongs to, none for a Swarm administrator.
        roles (List[RoleName]): The roles the person holds, without duplicates.
        PERSON_ID_FIELD (str): The name of the ``person_id`` field.
        OPERATOR_ID_FIELD (str): The name of the ``operator_id`` field.
        ROLES_FIELD (str): The name of the ``roles`` field.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **Every role except ``SWARM_ADMINISTRATOR`` needs an Operator**, and a Swarm administrator has none and holds
          no other role, so that it never reaches the data of an Operator (BR-008).
        - A caller without roles accepts any Operator, because no role is there to contradict it.
    """

    PERSON_ID_FIELD: ClassVar[str] = "person_id"
    OPERATOR_ID_FIELD: ClassVar[str] = "operator_id"
    ROLES_FIELD: ClassVar[str] = "roles"
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    person_id: UUID = Field(description="The person who calls.")
    operator_id: Optional[UUID] = Field(
        default=None, description="The Operator the person belongs to, none for a Swarm administrator."
    )
    roles: List[RoleName] = Field(default_factory=list, description="The roles the person holds.")

    @field_validator(PERSON_ID_FIELD, mode=BEFORE)
    def validate_person_id(cls, value: Union[JsonValue, UUID]) -> Union[JsonValue, UUID]:
        """Validate ``person_id``.

        Args:
            value (Union[JsonValue, UUID]): The raw input.

        Returns:
            Union[JsonValue, UUID]: The identifier.

        Raises:
            SECallerInvalidPersonId: If the value is not a UUID.
        """
        if isinstance(value, UUID):
            return value
        if not isinstance(value, str):
            raise SECallerInvalidPersonId(f"Invalid person_id: {value!r}. Must be a UUID.")
        try:
            return UUID(value.strip())
        except ValueError as error:
            raise SECallerInvalidPersonId(f"Invalid person_id: {value!r}. Must be a UUID.") from error

    @field_validator(OPERATOR_ID_FIELD, mode=BEFORE)
    def validate_operator_id(cls, value: Union[JsonValue, UUID]) -> Union[JsonValue, UUID]:
        """Validate ``operator_id``.

        Args:
            value (Union[JsonValue, UUID]): The raw input.

        Returns:
            Union[JsonValue, UUID]: The identifier, or ``None`` when there is none.

        Raises:
            SECallerInvalidOperatorId: If the value is not a UUID.
        """
        if value is None or isinstance(value, UUID):
            return value
        if not isinstance(value, str):
            raise SECallerInvalidOperatorId(f"Invalid operator_id: {value!r}. Must be a UUID.")
        try:
            return UUID(value.strip())
        except ValueError as error:
            raise SECallerInvalidOperatorId(f"Invalid operator_id: {value!r}. Must be a UUID.") from error

    @field_validator(ROLES_FIELD, mode=BEFORE)
    def validate_roles(cls, value: Union[JsonValue, List[RoleName]]) -> Union[JsonValue, List[RoleName]]:
        """Validate ``roles``.

        Args:
            value (Union[JsonValue, List[RoleName]]): The raw input.

        Returns:
            Union[JsonValue, List[RoleName]]: The roles, or an empty list when ``None``.

        Raises:
            SECallerInvalidRoles: If the value is not a list of distinct known roles.
        """
        if value is None:
            return []
        if not isinstance(value, list):
            raise SECallerInvalidRoles(f"Invalid roles: {value!r}. Must be a list of roles.")
        roles: List[RoleName] = []
        for item in value:
            if not isinstance(item, str):
                raise SECallerInvalidRoles(f"Invalid roles: {value!r}. Must hold only known roles.")
            try:
                role = RoleName(item)
            except ValueError as error:
                raise SECallerInvalidRoles(f"Invalid roles: {value!r}. Must hold only known roles.") from error
            if role in roles:
                raise SECallerInvalidRoles(f"Invalid roles: {value!r}. Must hold each role once.")
            roles.append(role)
        return roles

    @model_validator(mode="after")
    def validate_operator_and_roles(self) -> Caller:
        """Check that the Operator and the roles agree.

        Returns:
            Caller: This caller.

        Raises:
            SECallerOperatorMismatch: If a Swarm administrator has an Operator or another role, or if another role has
                no Operator.
        """
        if not self.roles:
            return self
        if RoleName.SWARM_ADMINISTRATOR in self.roles:
            if self.operator_id is not None or len(self.roles) > 1:
                raise SECallerOperatorMismatch(
                    f"Invalid roles: {self.roles!r}. Must be alone and without an Operator for a Swarm administrator."
                )
            return self
        if self.operator_id is None:
            raise SECallerOperatorMismatch(f"Invalid operator_id: {self.operator_id!r}. Must be set for these roles.")
        return self
