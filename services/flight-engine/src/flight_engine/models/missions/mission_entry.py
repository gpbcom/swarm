from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal, Self, Set
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from flight_engine.models.missions.drone_entry import DroneEntry
from flight_engine.models.missions.exceptions import (
    SEMissionEntryDuplicateDrone,
    SEMissionEntryDuplicateSystemId,
    SEMissionEntryInvalidDrones,
    SEMissionEntryInvalidMavlinkHost,
    SEMissionEntryInvalidMavlinkPort,
    SEMissionEntryInvalidMissionId,
    SEMissionEntryInvalidOperatorId,
)
from swarm_models.models.base.swarm_model import SwarmModel


class MissionEntry(SwarmModel):
    """One Mission of the Mission catalogue, with the MAVLink port its Drones send to.

    Attributes:
        operator_id (UUID): The Operator that owns the Mission, a version 7 UUID.
        mission_id (UUID): The Mission, a version 7 UUID.
        mavlink_host (str): The address the engine listens on for the Drones of the Mission.
        mavlink_port (int): The UDP port the engine listens on for the Drones of the Mission.
        drones (List[DroneEntry]): The Drones of the Mission, the only ones whose frames are read.
        OPERATOR_ID_FIELD (str): The name of the ``operator_id`` field, for its validator.
        MISSION_ID_FIELD (str): The name of the ``mission_id`` field, for its validator.
        MAVLINK_HOST_FIELD (str): The name of the ``mavlink_host`` field, for its validator.
        MAVLINK_PORT_FIELD (str): The name of the ``mavlink_port`` field, for its validator.
        DRONES_FIELD (str): The name of the ``drones`` field, for its validator.
        MAVLINK_PORT_MIN (int): The smallest port.
        MAVLINK_PORT_MAX (int): The largest port.
        DEFAULT_MAVLINK_HOST (str): The default address, every interface.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        AFTER (str): The validator mode that runs after Pydantic's own validation.

    Notes:
        A system id and a Drone id are each used once in a Mission, so a frame maps to one Drone.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    OPERATOR_ID_FIELD: ClassVar[str] = "operator_id"
    MISSION_ID_FIELD: ClassVar[str] = "mission_id"
    MAVLINK_HOST_FIELD: ClassVar[str] = "mavlink_host"
    MAVLINK_PORT_FIELD: ClassVar[str] = "mavlink_port"
    DRONES_FIELD: ClassVar[str] = "drones"
    MAVLINK_PORT_MIN: ClassVar[int] = 1
    MAVLINK_PORT_MAX: ClassVar[int] = 65535
    DEFAULT_MAVLINK_HOST: ClassVar[str] = "0.0.0.0"
    BEFORE: ClassVar[Literal["before"]] = "before"
    AFTER: ClassVar[Literal["after"]] = "after"

    operator_id: UUID = Field(description="The Operator that owns the Mission, a version 7 UUID.")
    mission_id: UUID = Field(description="The Mission, a version 7 UUID.")
    mavlink_host: str = Field(
        default=DEFAULT_MAVLINK_HOST,
        description="The address the engine listens on for the Drones of the Mission.",
    )
    mavlink_port: int = Field(description="The UDP port the engine listens on, from 1 to 65535.")
    drones: List[DroneEntry] = Field(description="The Drones of the Mission, each with its own system id.")

    @field_validator(OPERATOR_ID_FIELD, mode=BEFORE)
    def validate_operator_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``operator_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The version 7 UUID, as a string.

        Raises:
            SEMissionEntryInvalidOperatorId: If the value is not a version 7 UUID.
        """
        return str(cls.parse_uuid7(cls.OPERATOR_ID_FIELD, value, SEMissionEntryInvalidOperatorId))

    @field_validator(MISSION_ID_FIELD, mode=BEFORE)
    def validate_mission_id(cls, value: JsonValue) -> JsonValue:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The version 7 UUID, as a string.

        Raises:
            SEMissionEntryInvalidMissionId: If the value is not a version 7 UUID.
        """
        return str(cls.parse_uuid7(cls.MISSION_ID_FIELD, value, SEMissionEntryInvalidMissionId))

    @field_validator(MAVLINK_HOST_FIELD, mode=BEFORE)
    def validate_mavlink_host(cls, value: JsonValue) -> JsonValue:
        """Validate ``mavlink_host``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped address, or the default when ``None``.

        Raises:
            SEMissionEntryInvalidMavlinkHost: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_MAVLINK_HOST
        return cls.parse_text(cls.MAVLINK_HOST_FIELD, value, SEMissionEntryInvalidMavlinkHost)

    @field_validator(MAVLINK_PORT_FIELD, mode=BEFORE)
    def validate_mavlink_port(cls, value: JsonValue) -> JsonValue:
        """Validate ``mavlink_port``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The port.

        Raises:
            SEMissionEntryInvalidMavlinkPort: If the value is not an integer from 1 to 65535.
        """
        return cls.parse_int(
            cls.MAVLINK_PORT_FIELD,
            value,
            SEMissionEntryInvalidMavlinkPort,
            cls.MAVLINK_PORT_MIN,
            cls.MAVLINK_PORT_MAX,
        )

    @field_validator(DRONES_FIELD, mode=BEFORE)
    def validate_drones(cls, value: JsonValue) -> JsonValue:
        """Validate ``drones``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The list of Drones, left for Pydantic to build.

        Raises:
            SEMissionEntryInvalidDrones: If the value is not a list of mappings.
        """
        if not isinstance(value, list) or not all(isinstance(item, (dict, DroneEntry)) for item in value):
            raise SEMissionEntryInvalidDrones(f"Invalid drones: {value!r}. Must be a list of Drones.")
        return value

    @model_validator(mode=AFTER)
    def validate_unique_drones(self) -> Self:
        """Check that no system id and no Drone id is used twice.

        Returns:
            Self: The entry.

        Raises:
            SEMissionEntryDuplicateSystemId: If two Drones have the same system id.
            SEMissionEntryDuplicateDrone: If two Drones have the same Drone id.
        """
        system_ids: Set[int] = set()
        drone_ids: Set[UUID] = set()
        for drone in self.drones:
            if drone.system_id in system_ids:
                raise SEMissionEntryDuplicateSystemId(f"Duplicate system_id: {drone.system_id!r}. Must be used once.")
            if drone.drone_id in drone_ids:
                raise SEMissionEntryDuplicateDrone(f"Duplicate drone_id: {str(drone.drone_id)!r}. Must be used once.")
            system_ids.add(drone.system_id)
            drone_ids.add(drone.drone_id)
        return self
