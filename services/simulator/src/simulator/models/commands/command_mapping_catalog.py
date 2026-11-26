from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, Literal

# Third-party imports
from pydantic import Field, JsonValue, field_validator

# First-party imports
from simulator.models.commands.exceptions import (
    SECommandMappingCatalogInvalidCommands,
    SECommandMappingCatalogUnreadable,
)
from simulator.models.commands.mavlink_command_spec import MavlinkCommandSpec
from swarm_catalog.models.yaml_catalog import YamlCatalog
from swarm_models.commands.enums import CommandKind


class CommandMappingCatalog(YamlCatalog):
    """The catalogue that maps each Swarm command the Simulator accepts to a MAVLink command.

    Attributes:
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        COMMANDS_FIELD (str): The name of the ``commands`` field.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        commands (Dict[CommandKind, MavlinkCommandSpec]): The MAVLink command of each kind.

    Notes:
        - A kind missing from the catalogue is a kind the Simulator refuses.
    """

    UNREADABLE: ClassVar[type[Exception]] = SECommandMappingCatalogUnreadable
    COMMANDS_FIELD: ClassVar[str] = "commands"
    BEFORE: ClassVar[Literal["before"]] = "before"

    commands: Dict[CommandKind, MavlinkCommandSpec] = Field(description="The MAVLink command of each kind.")

    @field_validator(COMMANDS_FIELD, mode=BEFORE)
    def validate_commands(cls, value: JsonValue) -> JsonValue:
        """Validate ``commands``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The mapping, left to Pydantic to build.

        Raises:
            SECommandMappingCatalogInvalidCommands: If the value is not a non-empty mapping keyed by command kinds.
        """
        if not isinstance(value, dict) or not value:
            raise SECommandMappingCatalogInvalidCommands(f"Invalid commands: {value!r}. Must be a non-empty mapping.")
        known = [kind.value for kind in CommandKind]
        for key in value:
            if key not in known:
                raise SECommandMappingCatalogInvalidCommands(f"Invalid commands: {key!r}. Must be one of {known}.")
        return value
