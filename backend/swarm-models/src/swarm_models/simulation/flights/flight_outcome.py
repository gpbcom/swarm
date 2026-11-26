from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.enums import SimulatedDroneKind
from swarm_models.simulation.flights.exceptions import (
    SEFlightOutcomeInvalidCompleted,
    SEFlightOutcomeInvalidDroneId,
    SEFlightOutcomeInvalidElapsed,
    SEFlightOutcomeInvalidKind,
    SEFlightOutcomeInvalidWaypointsReached,
)


class FlightOutcome(SwarmModel):
    """What came of the flight of one simulated drone.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the outcome.
        drone_id (UUID): The Drone that flew.
        kind (SimulatedDroneKind): The kind of simulated drone.
        completed (bool): Whether the drone completed its route.
        waypoints_reached (int): How many waypoints the drone reached.
        elapsed_s (float): The duration of the flight, in seconds.
        DRONE_ID_FIELD (str): The name of the ``drone_id`` field, for its validator.
        KIND_FIELD (str): The name of the ``kind`` field, for its validator.
        COMPLETED_FIELD (str): The name of the ``completed`` field, for its validator.
        WAYPOINTS_REACHED_FIELD (str): The name of the ``waypoints_reached`` field, for its validator.
        ELAPSED_FIELD (str): The name of the ``elapsed_s`` field, for its validator.
        WAYPOINTS_REACHED_MIN (int): The smallest accepted count.
        ELAPSED_S_MIN (int): The smallest accepted duration.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **Booleans are refused wherever a number is expected**, and ``completed`` accepts only a boolean.
        - No field has a default, so ``None`` is refused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    DRONE_ID_FIELD: ClassVar[str] = "drone_id"
    KIND_FIELD: ClassVar[str] = "kind"
    COMPLETED_FIELD: ClassVar[str] = "completed"
    WAYPOINTS_REACHED_FIELD: ClassVar[str] = "waypoints_reached"
    ELAPSED_FIELD: ClassVar[str] = "elapsed_s"
    WAYPOINTS_REACHED_MIN: ClassVar[int] = 0
    ELAPSED_S_MIN: ClassVar[int] = 0
    BEFORE: ClassVar[Literal["before"]] = "before"

    drone_id: UUID = Field(description="The Drone that flew.")
    kind: SimulatedDroneKind = Field(description="The kind of simulated drone.")
    completed: bool = Field(description="Whether the drone completed its route.")
    waypoints_reached: int = Field(description="How many waypoints the drone reached.")
    elapsed_s: float = Field(description="The duration of the flight, in seconds.")

    ############################
    # Publicly Exposed Methods #
    ############################

    @field_validator(DRONE_ID_FIELD, mode=BEFORE)
    def validate_drone_id(cls, value: JsonValue) -> UUID:
        """Validate ``drone_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form.

        Returns:
            UUID: The UUID.

        Raises:
            SEFlightOutcomeInvalidDroneId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7(cls.DRONE_ID_FIELD, value, SEFlightOutcomeInvalidDroneId)

    @field_validator(KIND_FIELD, mode=BEFORE)
    def validate_kind(cls, value: JsonValue) -> SimulatedDroneKind:
        """Validate ``kind``.

        Args:
            value (JsonValue): A member of the enum or its value.

        Returns:
            SimulatedDroneKind: The member.

        Raises:
            SEFlightOutcomeInvalidKind: When the value is not a kind.
        """
        if isinstance(value, str):
            try:
                return SimulatedDroneKind(value)
            except ValueError:
                pass
        raise SEFlightOutcomeInvalidKind(
            f"Invalid {cls.KIND_FIELD}: {value!r}. Must be one of {[member.value for member in SimulatedDroneKind]}."
        )

    @field_validator(COMPLETED_FIELD, mode=BEFORE)
    def validate_completed(cls, value: JsonValue) -> bool:
        """Validate ``completed``.

        Args:
            value (JsonValue): A boolean.

        Returns:
            bool: The boolean.

        Raises:
            SEFlightOutcomeInvalidCompleted: When the value is not a boolean.
        """
        if not isinstance(value, bool):
            raise SEFlightOutcomeInvalidCompleted(f"Invalid {cls.COMPLETED_FIELD}: {value!r}. Must be a boolean.")
        return value

    @field_validator(WAYPOINTS_REACHED_FIELD, mode=BEFORE)
    def validate_waypoints_reached(cls, value: JsonValue) -> int:
        """Validate ``waypoints_reached``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SEFlightOutcomeInvalidWaypointsReached: When the value is not an integer within its bounds.
        """
        return cls.parse_int(
            cls.WAYPOINTS_REACHED_FIELD, value, SEFlightOutcomeInvalidWaypointsReached, cls.WAYPOINTS_REACHED_MIN, None
        )

    @field_validator(ELAPSED_FIELD, mode=BEFORE)
    def validate_elapsed_s(cls, value: JsonValue) -> float:
        """Validate ``elapsed_s``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            float: The finite number, within its bounds.

        Raises:
            SEFlightOutcomeInvalidElapsed: When the value is not a finite number within its bounds.
        """
        return cls.parse_float(cls.ELAPSED_FIELD, value, SEFlightOutcomeInvalidElapsed, cls.ELAPSED_S_MIN, None)
