from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from simulator.models.enums import SimulatedDroneKind
from simulator.models.registry.exceptions import (
    SERegisteredDroneInvalidDroneId,
    SERegisteredDroneInvalidHost,
    SERegisteredDroneInvalidKind,
    SERegisteredDroneInvalidPort,
    SERegisteredDroneInvalidSystemId,
)
from swarm_models.base.swarm_model import SwarmModel


class RegisteredDrone(SwarmModel):
    """One simulated Drone of the adapter registry, with the endpoint it is reached at.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the model.
        DRONE_ID_FIELD (str): The name of the ``drone_id`` field.
        KIND_FIELD (str): The name of the ``kind`` field.
        HOST_FIELD (str): The name of the ``host`` field.
        PORT_FIELD (str): The name of the ``port`` field.
        SYSTEM_ID_FIELD (str): The name of the ``system_id`` field.
        PORT_MIN (int): The smallest port.
        PORT_MAX (int): The largest port.
        SYSTEM_ID_MIN (int): The smallest MAVLink system id.
        SYSTEM_ID_MAX (int): The largest MAVLink system id.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        drone_id (UUID): The identifier of the Drone, a version 7 UUID.
        kind (SimulatedDroneKind): The kind of simulated Drone.
        host (str): The host the Drone is reached at.
        port (int): The port the Drone is reached at.
        system_id (int): The MAVLink system id of the Drone.

    Notes:
        - No field has a default, so ``None`` is refused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    DRONE_ID_FIELD: ClassVar[str] = "drone_id"
    KIND_FIELD: ClassVar[str] = "kind"
    HOST_FIELD: ClassVar[str] = "host"
    PORT_FIELD: ClassVar[str] = "port"
    SYSTEM_ID_FIELD: ClassVar[str] = "system_id"
    PORT_MIN: ClassVar[int] = 1
    PORT_MAX: ClassVar[int] = 65535
    SYSTEM_ID_MIN: ClassVar[int] = 1
    SYSTEM_ID_MAX: ClassVar[int] = 255
    BEFORE: ClassVar[Literal["before"]] = "before"

    drone_id: UUID = Field(description="The identifier of the Drone, a version 7 UUID.")
    kind: SimulatedDroneKind = Field(description="The kind of simulated Drone.")
    host: str = Field(description="The host the Drone is reached at.")
    port: int = Field(description="The port the Drone is reached at.")
    system_id: int = Field(description="The MAVLink system id of the Drone.")

    @field_validator(DRONE_ID_FIELD, mode=BEFORE)
    def validate_drone_id(cls, value: JsonValue) -> UUID:
        """Validate ``drone_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            UUID: The version 7 UUID.

        Raises:
            SERegisteredDroneInvalidDroneId: If the value is not a version 7 UUID.
        """
        return cls.parse_uuid7(cls.DRONE_ID_FIELD, value, SERegisteredDroneInvalidDroneId)

    @field_validator(KIND_FIELD, mode=BEFORE)
    def validate_kind(cls, value: JsonValue) -> SimulatedDroneKind:
        """Validate ``kind``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            SimulatedDroneKind: The kind.

        Raises:
            SERegisteredDroneInvalidKind: If the value is not a kind of simulated Drone.
        """
        if not isinstance(value, str) or value not in SimulatedDroneKind:
            raise SERegisteredDroneInvalidKind(
                f"Invalid kind: {value!r}. Must be one of {[kind.value for kind in SimulatedDroneKind]}."
            )
        return SimulatedDroneKind(value)

    @field_validator(HOST_FIELD, mode=BEFORE)
    def validate_host(cls, value: JsonValue) -> str:
        """Validate ``host``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            str: The stripped host.

        Raises:
            SERegisteredDroneInvalidHost: If the value is not a non-empty string.
        """
        return cls.parse_text(cls.HOST_FIELD, value, SERegisteredDroneInvalidHost)

    @field_validator(PORT_FIELD, mode=BEFORE)
    def validate_port(cls, value: JsonValue) -> int:
        """Validate ``port``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            int: The port.

        Raises:
            SERegisteredDroneInvalidPort: If the value is not an integer in the bounds.
        """
        return cls.parse_int(cls.PORT_FIELD, value, SERegisteredDroneInvalidPort, cls.PORT_MIN, cls.PORT_MAX)

    @field_validator(SYSTEM_ID_FIELD, mode=BEFORE)
    def validate_system_id(cls, value: JsonValue) -> int:
        """Validate ``system_id``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            int: The system id.

        Raises:
            SERegisteredDroneInvalidSystemId: If the value is not an integer in the bounds.
        """
        return cls.parse_int(
            cls.SYSTEM_ID_FIELD, value, SERegisteredDroneInvalidSystemId, cls.SYSTEM_ID_MIN, cls.SYSTEM_ID_MAX
        )
