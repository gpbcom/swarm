from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Optional
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from simulator.models.enums import FlightLogEntryKind
from simulator.models.flight_logs.exceptions import (
    SEFlightLogEntryInvalidDetail,
    SEFlightLogEntryInvalidDroneId,
    SEFlightLogEntryInvalidKind,
    SEFlightLogEntryInvalidMissionId,
    SEFlightLogEntryInvalidSeq,
    SEFlightLogEntryInvalidTUs,
    SEFlightLogEntryNotSimulated,
)
from swarm_models.base.swarm_model import SwarmModel


class FlightLogEntry(SwarmModel):
    """One line of the Flight log of a simulated flight.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the entry.
        mission_id (UUID): The Mission the entry belongs to.
        drone_id (Optional[UUID]): The Drone concerned, or None for the whole Squad.
        t_us (int): The moment of the entry, in microseconds since the epoch.
        kind (FlightLogEntryKind): What happened.
        seq (Optional[int]): The sequence number per Drone, when there is one.
        detail (Optional[str]): A short text, when there is one.
        simulated (bool): Whether the entry comes from a simulated flight, which it always does.
        MISSION_ID_FIELD (str): The name of the ``mission_id`` field, for its validator.
        DRONE_ID_FIELD (str): The name of the ``drone_id`` field, for its validator.
        T_US_FIELD (str): The name of the ``t_us`` field, for its validator.
        KIND_FIELD (str): The name of the ``kind`` field, for its validator.
        SEQ_FIELD (str): The name of the ``seq`` field, for its validator.
        DETAIL_FIELD (str): The name of the ``detail`` field, for its validator.
        SIMULATED_FIELD (str): The name of the ``simulated`` field, for its validator.
        T_US_MIN (int): The smallest accepted moment.
        SEQ_MIN (int): The smallest accepted sequence number.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - **BR-014 requires the Flight log of a simulated Squad to be marked as simulated**, so ``simulated`` is
          ``True`` by default and ``False`` raises ``SEFlightLogEntryNotSimulated``.
        - This model stays local to the Simulator until the flight engine owns the shared ``FlightLogEntry`` of
          ``docs/specs/technical/02-data-models.md#models``.
        - **Booleans are refused wherever a number is expected.**
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    MISSION_ID_FIELD: ClassVar[str] = "mission_id"
    DRONE_ID_FIELD: ClassVar[str] = "drone_id"
    T_US_FIELD: ClassVar[str] = "t_us"
    KIND_FIELD: ClassVar[str] = "kind"
    SEQ_FIELD: ClassVar[str] = "seq"
    DETAIL_FIELD: ClassVar[str] = "detail"
    SIMULATED_FIELD: ClassVar[str] = "simulated"
    T_US_MIN: ClassVar[int] = 0
    SEQ_MIN: ClassVar[int] = 0
    BEFORE: ClassVar[Literal["before"]] = "before"

    mission_id: UUID = Field(description="The Mission the entry belongs to.")
    drone_id: Optional[UUID] = Field(default=None, description="The Drone concerned, or None for the whole Squad.")
    t_us: int = Field(description="The moment of the entry, in microseconds since the epoch.")
    kind: FlightLogEntryKind = Field(description="What happened.")
    seq: Optional[int] = Field(default=None, description="The sequence number per Drone, when there is one.")
    detail: Optional[str] = Field(default=None, description="A short text, when there is one.")
    simulated: bool = Field(default=True, description="Whether the entry comes from a simulated flight.")

    ############################
    # Publicly Exposed Methods #
    ############################

    @field_validator(MISSION_ID_FIELD, mode=BEFORE)
    def validate_mission_id(cls, value: JsonValue) -> UUID:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form.

        Returns:
            UUID: The UUID.

        Raises:
            SEFlightLogEntryInvalidMissionId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7(cls.MISSION_ID_FIELD, value, SEFlightLogEntryInvalidMissionId)

    @field_validator(DRONE_ID_FIELD, mode=BEFORE)
    def validate_drone_id(cls, value: JsonValue) -> Optional[UUID]:
        """Validate ``drone_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form, or None.

        Returns:
            Optional[UUID]: The UUID, or None.

        Raises:
            SEFlightLogEntryInvalidDroneId: When the value is not None or a version 7 UUID.
        """
        if value is None:
            return None
        return cls.parse_uuid7(cls.DRONE_ID_FIELD, value, SEFlightLogEntryInvalidDroneId)

    @field_validator(T_US_FIELD, mode=BEFORE)
    def validate_t_us(cls, value: JsonValue) -> int:
        """Validate ``t_us``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SEFlightLogEntryInvalidTUs: When the value is not an integer within its bounds.
        """
        return cls.parse_int(cls.T_US_FIELD, value, SEFlightLogEntryInvalidTUs, cls.T_US_MIN, None)

    @field_validator(KIND_FIELD, mode=BEFORE)
    def validate_kind(cls, value: JsonValue) -> FlightLogEntryKind:
        """Validate ``kind``.

        Args:
            value (JsonValue): A member of the enum or its value.

        Returns:
            FlightLogEntryKind: The member.

        Raises:
            SEFlightLogEntryInvalidKind: When the value is not a kind.
        """
        if isinstance(value, str):
            try:
                return FlightLogEntryKind(value)
            except ValueError:
                pass
        raise SEFlightLogEntryInvalidKind(
            f"Invalid {cls.KIND_FIELD}: {value!r}. Must be one of {[member.value for member in FlightLogEntryKind]}."
        )

    @field_validator(SEQ_FIELD, mode=BEFORE)
    def validate_seq(cls, value: JsonValue) -> Optional[int]:
        """Validate ``seq``.

        Args:
            value (JsonValue): The raw value, or None.

        Returns:
            Optional[int]: The integer, or None.

        Raises:
            SEFlightLogEntryInvalidSeq: When the value is not None or an integer within its bounds.
        """
        if value is None:
            return None
        return cls.parse_int(cls.SEQ_FIELD, value, SEFlightLogEntryInvalidSeq, cls.SEQ_MIN, None)

    @field_validator(DETAIL_FIELD, mode=BEFORE)
    def validate_detail(cls, value: JsonValue) -> Optional[str]:
        """Validate ``detail``.

        Args:
            value (JsonValue): The raw value, or None.

        Returns:
            Optional[str]: The stripped text, or None.

        Raises:
            SEFlightLogEntryInvalidDetail: When the value is not None or a non-empty string.
        """
        if value is None:
            return None
        return cls.parse_text(cls.DETAIL_FIELD, value, SEFlightLogEntryInvalidDetail)

    @field_validator(SIMULATED_FIELD, mode=BEFORE)
    def validate_simulated(cls, value: JsonValue) -> bool:
        """Validate ``simulated``.

        Args:
            value (JsonValue): True, or None for the default.

        Returns:
            bool: Always True.

        Raises:
            SEFlightLogEntryNotSimulated: When the value is not True.
        """
        if value is None or value is True:
            return True
        raise SEFlightLogEntryNotSimulated(
            f"Invalid {cls.SIMULATED_FIELD}: {value!r}. "
            "Must be True, as BR-014 requires the Flight log of a simulated Squad to be marked as simulated."
        )
