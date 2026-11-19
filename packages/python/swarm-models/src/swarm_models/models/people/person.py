from __future__ import annotations

# Standard library imports
from typing import ClassVar, Optional
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.models.base.swarm_model import SwarmModel
from swarm_models.models.people.exceptions import (
    SEPersonInvalidEmail,
    SEPersonInvalidId,
    SEPersonInvalidName,
    SEPersonInvalidOperatorId,
)


class Person(SwarmModel):
    """A person known to Swarm.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        id (UUID): The version 7 identifier of the person.
        operator_id (Optional[UUID]): The Operator the person belongs to, ``None`` for a Swarm administrator.
        name (str): The full name of the person.
        email (str): The email address of the person.
        EMAIL_SEPARATOR (ClassVar[str]): The character that splits an email address into its local part and domain.

    Notes:
        The email check is structural only: one separator, a local part and a domain, and no whitespace.
    """

    model_config = ConfigDict(extra="forbid")

    EMAIL_SEPARATOR: ClassVar[str] = "@"

    id: UUID = Field(description="The version 7 identifier of the person.")
    operator_id: Optional[UUID] = Field(default=None, description="The Operator the person belongs to, if any.")
    name: str = Field(description="The full name of the person.")
    email: str = Field(description="The email address of the person.")

    @field_validator("id", mode="before")
    def validate_id(cls, value: JsonValue) -> UUID:
        """Validate ``id``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            UUID: The version 7 UUID.
        """
        return cls.parse_uuid7("id", value, SEPersonInvalidId)

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
        return cls.parse_uuid7("operator_id", value, SEPersonInvalidOperatorId)

    @field_validator("name", mode="before")
    def validate_name(cls, value: JsonValue) -> str:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped name.
        """
        return cls.parse_text("name", value, SEPersonInvalidName)

    @field_validator("email", mode="before")
    def validate_email(cls, value: JsonValue) -> str:
        """Validate ``email``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            str: The stripped email address.

        Raises:
            SEPersonInvalidEmail: When the address is not a local part and a domain around one separator.
        """
        email = cls.parse_text("email", value, SEPersonInvalidEmail)
        local, separator, domain = email.partition(cls.EMAIL_SEPARATOR)
        if not separator or not local or not domain or cls.EMAIL_SEPARATOR in domain or any(c.isspace() for c in email):
            raise SEPersonInvalidEmail(
                f"Invalid email: {value!r}. Must be a local part and a domain around one separator, with no whitespace."
            )
        return email
