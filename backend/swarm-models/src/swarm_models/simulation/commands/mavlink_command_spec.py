from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.simulation.commands.exceptions import (
    SEMavlinkCommandSpecInvalidCommandId,
    SEMavlinkCommandSpecInvalidParam1,
)


class MavlinkCommandSpec(SwarmModel):
    """The MAVLink command a Swarm command is sent as.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the model.
        COMMAND_ID_FIELD (str): The name of the ``command_id`` field.
        PARAM1_FIELD (str): The name of the ``param1`` field.
        COMMAND_ID_MIN (int): The smallest MAVLink command id.
        COMMAND_ID_MAX (int): The largest MAVLink command id.
        DEFAULT_PARAM1 (float): The default first parameter.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        command_id (int): The MAVLink command id.
        param1 (float): The first parameter of the command.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    COMMAND_ID_FIELD: ClassVar[str] = "command_id"
    PARAM1_FIELD: ClassVar[str] = "param1"
    COMMAND_ID_MIN: ClassVar[int] = 0
    COMMAND_ID_MAX: ClassVar[int] = 65535
    DEFAULT_PARAM1: ClassVar[float] = 0.0
    BEFORE: ClassVar[Literal["before"]] = "before"

    command_id: int = Field(description="The MAVLink command id.")
    param1: float = Field(default=DEFAULT_PARAM1, description="The first parameter of the command.")

    @field_validator(COMMAND_ID_FIELD, mode=BEFORE)
    def validate_command_id(cls, value: JsonValue) -> int:
        """Validate ``command_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            int: The command id.

        Raises:
            SEMavlinkCommandSpecInvalidCommandId: If the value is not an integer in the bounds.
        """
        return cls.parse_int(
            cls.COMMAND_ID_FIELD,
            value,
            SEMavlinkCommandSpecInvalidCommandId,
            cls.COMMAND_ID_MIN,
            cls.COMMAND_ID_MAX,
        )

    @field_validator(PARAM1_FIELD, mode=BEFORE)
    def validate_param1(cls, value: JsonValue) -> float:
        """Validate ``param1``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            float: The first parameter, or the default when ``None``.

        Raises:
            SEMavlinkCommandSpecInvalidParam1: If the value is not a finite number.
        """
        if value is None:
            return cls.DEFAULT_PARAM1
        return cls.parse_float(cls.PARAM1_FIELD, value, SEMavlinkCommandSpecInvalidParam1)
