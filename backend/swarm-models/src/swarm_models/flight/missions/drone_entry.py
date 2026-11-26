from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.flight.missions.exceptions import SEDroneEntryInvalidDroneId, SEDroneEntryInvalidSystemId


class DroneEntry(SwarmModel):
    """One Drone of a Mission, as the Mission catalogue lists it.

    Attributes:
        system_id (int): The MAVLink system id the Drone sends its frames with.
        drone_id (UUID): The identifier of the Drone, a version 7 UUID.
        SYSTEM_ID_FIELD (str): The name of the ``system_id`` field, for its validator.
        DRONE_ID_FIELD (str): The name of the ``drone_id`` field, for its validator.
        SYSTEM_ID_MIN (int): The smallest system id.
        SYSTEM_ID_MAX (int): The largest system id.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        Both fields are required: a Drone without its ids cannot be told apart in a frame.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    SYSTEM_ID_FIELD: ClassVar[str] = "system_id"
    DRONE_ID_FIELD: ClassVar[str] = "drone_id"
    SYSTEM_ID_MIN: ClassVar[int] = 1
    SYSTEM_ID_MAX: ClassVar[int] = 255
    BEFORE: ClassVar[Literal["before"]] = "before"

    system_id: int = Field(description="The MAVLink system id of the Drone, from 1 to 255.")
    drone_id: UUID = Field(description="The identifier of the Drone, a version 7 UUID.")

    @field_validator(SYSTEM_ID_FIELD, mode=BEFORE)
    def validate_system_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``system_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The system id.

        Raises:
            SEDroneEntryInvalidSystemId: If the value is not an integer from 1 to 255.
        """
        return cls.parse_int(
            cls.SYSTEM_ID_FIELD, value, SEDroneEntryInvalidSystemId, cls.SYSTEM_ID_MIN, cls.SYSTEM_ID_MAX
        )

    @field_validator(DRONE_ID_FIELD, mode=BEFORE)
    def validate_drone_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``drone_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The version 7 UUID, as a string.

        Raises:
            SEDroneEntryInvalidDroneId: If the value is not a version 7 UUID.
        """
        return str(cls.parse_uuid7(cls.DRONE_ID_FIELD, value, SEDroneEntryInvalidDroneId))
