from __future__ import annotations

# Standard library imports
from typing import ClassVar
from uuid import UUID

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.telemetry.enums import DroneState
from swarm_models.telemetry.exceptions import (
    SETelemetryFrameInvalidAltitudeM,
    SETelemetryFrameInvalidBatteryPct,
    SETelemetryFrameInvalidDroneId,
    SETelemetryFrameInvalidHeadingDeg,
    SETelemetryFrameInvalidLatE7,
    SETelemetryFrameInvalidLinkQualityPct,
    SETelemetryFrameInvalidLonE7,
    SETelemetryFrameInvalidMissionId,
    SETelemetryFrameInvalidSeq,
    SETelemetryFrameInvalidSpeedMS,
    SETelemetryFrameInvalidState,
    SETelemetryFrameInvalidTUs,
)


class TelemetryFrame(SwarmModel):
    """What one Drone reports at one tick.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the frame.
        mission_id (UUID): The Mission the frame belongs to.
        drone_id (UUID): The Drone that sent the frame.
        seq (int): The sequence number per Drone, which detects gaps.
        t_us (int): The moment of the frame, in microseconds since the epoch.
        lat_e7 (int): The latitude in degrees multiplied by 1e7.
        lon_e7 (int): The longitude in degrees multiplied by 1e7.
        altitude_m (float): The altitude, in metres.
        speed_m_s (float): The speed, in metres per second.
        heading_deg (float): The heading, in degrees from north.
        battery_pct (float): The battery charge, in percent.
        link_quality_pct (float): The quality of the Link, in percent.
        state (DroneState): The state of the Drone.
        LAT_E7_MIN (ClassVar[int]): The smallest accepted value.
        LAT_E7_MAX (ClassVar[int]): The largest accepted value.
        LON_E7_MIN (ClassVar[int]): The smallest accepted value.
        LON_E7_MAX (ClassVar[int]): The largest accepted value.
        SEQ_MIN (ClassVar[int]): The smallest accepted value.
        T_US_MIN (ClassVar[int]): The smallest accepted value.
        SPEED_M_S_MIN (ClassVar[int]): The smallest accepted value.
        HEADING_DEG_MIN (ClassVar[int]): The smallest accepted value.
        HEADING_DEG_MAX (ClassVar[int]): The largest accepted value, which is excluded.
        BATTERY_PCT_MIN (ClassVar[int]): The smallest accepted value.
        BATTERY_PCT_MAX (ClassVar[int]): The largest accepted value.
        LINK_QUALITY_PCT_MIN (ClassVar[int]): The smallest accepted value.
        LINK_QUALITY_PCT_MAX (ClassVar[int]): The largest accepted value.

    Notes:
        - Latitude and longitude are integers, so that frames stay small.
        - **Booleans are refused wherever a number is expected.**
        - ``payload_state`` is not part of this version of the frame.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    LAT_E7_MIN: ClassVar[int] = -900000000
    LAT_E7_MAX: ClassVar[int] = 900000000
    LON_E7_MIN: ClassVar[int] = -1800000000
    LON_E7_MAX: ClassVar[int] = 1800000000
    SEQ_MIN: ClassVar[int] = 0
    T_US_MIN: ClassVar[int] = 0
    SPEED_M_S_MIN: ClassVar[int] = 0
    HEADING_DEG_MIN: ClassVar[int] = 0
    HEADING_DEG_MAX: ClassVar[int] = 360
    BATTERY_PCT_MIN: ClassVar[int] = 0
    BATTERY_PCT_MAX: ClassVar[int] = 100
    LINK_QUALITY_PCT_MIN: ClassVar[int] = 0
    LINK_QUALITY_PCT_MAX: ClassVar[int] = 100

    mission_id: UUID = Field(description="The Mission the frame belongs to.")
    drone_id: UUID = Field(description="The Drone that sent the frame.")
    seq: int = Field(description="The sequence number per Drone, which detects gaps.")
    t_us: int = Field(description="The moment of the frame, in microseconds since the epoch.")
    lat_e7: int = Field(description="The latitude in degrees multiplied by 1e7.")
    lon_e7: int = Field(description="The longitude in degrees multiplied by 1e7.")
    altitude_m: float = Field(description="The altitude, in metres.")
    speed_m_s: float = Field(description="The speed, in metres per second.")
    heading_deg: float = Field(description="The heading, in degrees from north.")
    battery_pct: float = Field(description="The battery charge, in percent.")
    link_quality_pct: float = Field(description="The quality of the Link, in percent.")
    state: DroneState = Field(description="The state of the Drone.")

    ############################
    # Publicly Exposed Methods #
    ############################

    @field_validator("mission_id", mode="before")
    def validate_mission_id(cls, value: JsonValue) -> UUID:
        """Validate ``mission_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form.

        Returns:
            UUID: The UUID.

        Raises:
            SETelemetryFrameInvalidMissionId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7("mission_id", value, SETelemetryFrameInvalidMissionId)

    @field_validator("drone_id", mode="before")
    def validate_drone_id(cls, value: JsonValue) -> UUID:
        """Validate ``drone_id``.

        Args:
            value (JsonValue): A version 7 UUID or its string form.

        Returns:
            UUID: The UUID.

        Raises:
            SETelemetryFrameInvalidDroneId: When the value is not a version 7 UUID.
        """
        return cls.parse_uuid7("drone_id", value, SETelemetryFrameInvalidDroneId)

    @field_validator("seq", mode="before")
    def validate_seq(cls, value: JsonValue) -> int:
        """Validate ``seq``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SETelemetryFrameInvalidSeq: When the value is not an integer within its bounds.
        """
        return cls.parse_int("seq", value, SETelemetryFrameInvalidSeq, cls.SEQ_MIN, None)

    @field_validator("t_us", mode="before")
    def validate_t_us(cls, value: JsonValue) -> int:
        """Validate ``t_us``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SETelemetryFrameInvalidTUs: When the value is not an integer within its bounds.
        """
        return cls.parse_int("t_us", value, SETelemetryFrameInvalidTUs, cls.T_US_MIN, None)

    @field_validator("lat_e7", mode="before")
    def validate_lat_e7(cls, value: JsonValue) -> int:
        """Validate ``lat_e7``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SETelemetryFrameInvalidLatE7: When the value is not an integer within its bounds.
        """
        return cls.parse_int("lat_e7", value, SETelemetryFrameInvalidLatE7, cls.LAT_E7_MIN, cls.LAT_E7_MAX)

    @field_validator("lon_e7", mode="before")
    def validate_lon_e7(cls, value: JsonValue) -> int:
        """Validate ``lon_e7``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SETelemetryFrameInvalidLonE7: When the value is not an integer within its bounds.
        """
        return cls.parse_int("lon_e7", value, SETelemetryFrameInvalidLonE7, cls.LON_E7_MIN, cls.LON_E7_MAX)

    @field_validator("altitude_m", mode="before")
    def validate_altitude_m(cls, value: JsonValue) -> float:
        """Validate ``altitude_m``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            float: The number, within its bounds.

        Raises:
            SETelemetryFrameInvalidAltitudeM: When the value is not a finite number within its bounds.
        """
        return cls.parse_float("altitude_m", value, SETelemetryFrameInvalidAltitudeM, None, None)

    @field_validator("speed_m_s", mode="before")
    def validate_speed_m_s(cls, value: JsonValue) -> float:
        """Validate ``speed_m_s``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            float: The number, within its bounds.

        Raises:
            SETelemetryFrameInvalidSpeedMS: When the value is not a finite number within its bounds.
        """
        return cls.parse_float("speed_m_s", value, SETelemetryFrameInvalidSpeedMS, cls.SPEED_M_S_MIN, None)

    @field_validator("heading_deg", mode="before")
    def validate_heading_deg(cls, value: JsonValue) -> float:
        """Validate ``heading_deg``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            float: The number, within its bounds.

        Raises:
            SETelemetryFrameInvalidHeadingDeg: When the value is not a finite number within its bounds.
        """
        return cls.parse_float(
            "heading_deg",
            value,
            SETelemetryFrameInvalidHeadingDeg,
            cls.HEADING_DEG_MIN,
            cls.HEADING_DEG_MAX,
            maximum_exclusive=True,
        )

    @field_validator("battery_pct", mode="before")
    def validate_battery_pct(cls, value: JsonValue) -> float:
        """Validate ``battery_pct``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            float: The number, within its bounds.

        Raises:
            SETelemetryFrameInvalidBatteryPct: When the value is not a finite number within its bounds.
        """
        return cls.parse_float(
            "battery_pct", value, SETelemetryFrameInvalidBatteryPct, cls.BATTERY_PCT_MIN, cls.BATTERY_PCT_MAX
        )

    @field_validator("link_quality_pct", mode="before")
    def validate_link_quality_pct(cls, value: JsonValue) -> float:
        """Validate ``link_quality_pct``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            float: The number, within its bounds.

        Raises:
            SETelemetryFrameInvalidLinkQualityPct: When the value is not a finite number within its bounds.
        """
        return cls.parse_float(
            "link_quality_pct",
            value,
            SETelemetryFrameInvalidLinkQualityPct,
            cls.LINK_QUALITY_PCT_MIN,
            cls.LINK_QUALITY_PCT_MAX,
        )

    @field_validator("state", mode="before")
    def validate_state(cls, value: JsonValue) -> DroneState:
        """Validate ``state``.

        Args:
            value (JsonValue): A ``DroneState`` or its string value.

        Returns:
            DroneState: The state.

        Raises:
            SETelemetryFrameInvalidState: When the value is not a Drone state.
        """
        if isinstance(value, DroneState):
            return value
        if isinstance(value, str):
            try:
                return DroneState(value)
            except ValueError:
                pass
        raise SETelemetryFrameInvalidState(
            f"Invalid state: {value!r}. Must be one of {[member.value for member in DroneState]}."
        )
