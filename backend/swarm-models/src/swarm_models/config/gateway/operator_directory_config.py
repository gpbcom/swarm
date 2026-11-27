from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, Literal, Pattern, Union

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.config.gateway.exceptions import (
    SEOperatorDirectoryConfigInvalidCell,
    SEOperatorDirectoryConfigInvalidKeycloak,
)
from swarm_models.keycloak.keycloak_admin_config import KeycloakAdminConfig


class OperatorDirectoryConfig(BaseModel):
    """The configuration of the Operator directory of the gateway.

    Attributes:
        cell (str): The cell a new Operator is placed in.
        keycloak (KeycloakAdminConfig): The calls to the Keycloak admin API.
        CELL_FIELD (str): The name of the ``cell`` field.
        KEYCLOAK_FIELD (str): The name of the ``keycloak`` field.
        DEFAULT_CELL (str): The default cell.
        CELL_PATTERN (Pattern[str]): Lower case letters, digits and underscores, starting with a letter.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - The nested ``keycloak`` section is validated by its own model, and its errors are raised unchanged.
    """

    CELL_FIELD: ClassVar[str] = "cell"
    KEYCLOAK_FIELD: ClassVar[str] = "keycloak"
    DEFAULT_CELL: ClassVar[str] = "dev"
    CELL_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[a-z][a-z0-9_]*$")
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    cell: str = Field(default=DEFAULT_CELL, description="The cell a new Operator is placed in. Defaults to dev.")
    keycloak: KeycloakAdminConfig = Field(
        default_factory=KeycloakAdminConfig, description="The calls to the Keycloak admin API."
    )

    @field_validator(CELL_FIELD, mode=BEFORE)
    def validate_cell(cls, value: JsonValue) -> JsonValue:
        """Validate ``cell``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped cell, or the default when ``None``.

        Raises:
            SEOperatorDirectoryConfigInvalidCell: If the value is not a lower case identifier.
        """
        if value is None:
            return cls.DEFAULT_CELL
        if not isinstance(value, str) or not cls.CELL_PATTERN.match(value.strip()):
            raise SEOperatorDirectoryConfigInvalidCell(
                f"Invalid cell: {value!r}. Must be lower case letters, digits and underscores, starting with a letter."
            )
        return value.strip()

    @field_validator(KEYCLOAK_FIELD, mode=BEFORE)
    def validate_keycloak(cls, value: Union[JsonValue, KeycloakAdminConfig]) -> Union[JsonValue, KeycloakAdminConfig]:
        """Validate ``keycloak``.

        Args:
            value (Union[JsonValue, KeycloakAdminConfig]): The raw input.

        Returns:
            Union[JsonValue, KeycloakAdminConfig]: The section, or the default section when ``None``.

        Raises:
            SEOperatorDirectoryConfigInvalidKeycloak: If the value is not a mapping.
        """
        if value is None:
            return cls.model_fields[cls.KEYCLOAK_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (dict, KeycloakAdminConfig)):
            raise SEOperatorDirectoryConfigInvalidKeycloak(f"Invalid keycloak: {value!r}. Must be a mapping.")
        return value
