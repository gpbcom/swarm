from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, Literal, Optional, Tuple, Type

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, ValidationInfo, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.flight.telemetry.exceptions import (
    SEDroneSampleInvalidBaseMode,
    SEDroneSampleInvalidBatteryRemaining,
    SEDroneSampleInvalidHasPosition,
    SEDroneSampleInvalidHdgCdeg,
    SEDroneSampleInvalidLatE7,
    SEDroneSampleInvalidLonE7,
    SEDroneSampleInvalidLost,
    SEDroneSampleInvalidReceived,
    SEDroneSampleInvalidRelativeAltMm,
    SEDroneSampleInvalidSystemId,
    SEDroneSampleInvalidSystemStatus,
    SEDroneSampleInvalidUpdatedAtUs,
    SEDroneSampleInvalidVxCmS,
    SEDroneSampleInvalidVyCmS,
)


class DroneSample(SwarmModel):
    """The latest sample of one Drone, as the Rust MAVLink core hands it over.

    Attributes:
        system_id (int): The MAVLink system id of the Drone.
        has_position (bool): Whether the position fields hold a fix.
        lat_e7 (int): The latitude in degrees times 10^7.
        lon_e7 (int): The longitude in degrees times 10^7.
        relative_alt_mm (int): The altitude above the take-off point, in millimetres.
        vx_cm_s (int): The ground speed to the north, in centimetres per second.
        vy_cm_s (int): The ground speed to the east, in centimetres per second.
        hdg_cdeg (int): The heading in centidegrees.
        battery_remaining (int): The battery charge in percent, -1 when unknown.
        base_mode (int): The MAVLink base mode bits.
        system_status (int): The MAVLink system status.
        received (int): The number of frames received from the Drone.
        lost (int): The number of frames lost, from the gaps of the sequence numbers.
        updated_at_us (int): When the sample was last updated, in microseconds.
        SYSTEM_ID_FIELD (str): The name of the ``system_id`` field.
        HAS_POSITION_FIELD (str): The name of the ``has_position`` field.
        LAT_E7_FIELD (str): The name of the ``lat_e7`` field.
        LON_E7_FIELD (str): The name of the ``lon_e7`` field.
        RELATIVE_ALT_MM_FIELD (str): The name of the ``relative_alt_mm`` field.
        VX_CM_S_FIELD (str): The name of the ``vx_cm_s`` field.
        VY_CM_S_FIELD (str): The name of the ``vy_cm_s`` field.
        HDG_CDEG_FIELD (str): The name of the ``hdg_cdeg`` field.
        BATTERY_REMAINING_FIELD (str): The name of the ``battery_remaining`` field.
        BASE_MODE_FIELD (str): The name of the ``base_mode`` field.
        SYSTEM_STATUS_FIELD (str): The name of the ``system_status`` field.
        RECEIVED_FIELD (str): The name of the ``received`` field.
        LOST_FIELD (str): The name of the ``lost`` field.
        UPDATED_AT_US_FIELD (str): The name of the ``updated_at_us`` field.
        SYSTEM_ID_MIN (int): The smallest system id.
        SYSTEM_ID_MAX (int): The largest system id.
        I32_MIN (int): The smallest signed 32-bit integer, the bound of the position fields.
        I32_MAX (int): The largest signed 32-bit integer.
        I16_MIN (int): The smallest signed 16-bit integer, the bound of the speed fields.
        I16_MAX (int): The largest signed 16-bit integer.
        HDG_CDEG_MIN (int): The smallest heading.
        HDG_CDEG_MAX (int): The largest unsigned 16-bit integer.
        BATTERY_REMAINING_MIN (int): The unknown battery, -1.
        BATTERY_REMAINING_MAX (int): The full battery, 100.
        U8_MIN (int): The smallest unsigned 8-bit integer.
        U8_MAX (int): The largest unsigned 8-bit integer, the bound of the mode and the status.
        COUNTER_MIN (int): The smallest counter or time.
        INTEGER_BOUNDS (Dict[str, Tuple[int, Optional[int]]]): The bounds of each integer field, by field name.
        INTEGER_ERRORS (Dict[str, Type[Exception]]): The exception of each integer field, by field name.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - The integer bounds are those of the Rust sample's types, so a value that fits no type is refused here.
        - A sample never changes: the engine replaces it with the next one.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    SYSTEM_ID_FIELD: ClassVar[str] = "system_id"
    HAS_POSITION_FIELD: ClassVar[str] = "has_position"
    LAT_E7_FIELD: ClassVar[str] = "lat_e7"
    LON_E7_FIELD: ClassVar[str] = "lon_e7"
    RELATIVE_ALT_MM_FIELD: ClassVar[str] = "relative_alt_mm"
    VX_CM_S_FIELD: ClassVar[str] = "vx_cm_s"
    VY_CM_S_FIELD: ClassVar[str] = "vy_cm_s"
    HDG_CDEG_FIELD: ClassVar[str] = "hdg_cdeg"
    BATTERY_REMAINING_FIELD: ClassVar[str] = "battery_remaining"
    BASE_MODE_FIELD: ClassVar[str] = "base_mode"
    SYSTEM_STATUS_FIELD: ClassVar[str] = "system_status"
    RECEIVED_FIELD: ClassVar[str] = "received"
    LOST_FIELD: ClassVar[str] = "lost"
    UPDATED_AT_US_FIELD: ClassVar[str] = "updated_at_us"
    SYSTEM_ID_MIN: ClassVar[int] = 1
    SYSTEM_ID_MAX: ClassVar[int] = 255
    I32_MIN: ClassVar[int] = -(2**31)
    I32_MAX: ClassVar[int] = 2**31 - 1
    I16_MIN: ClassVar[int] = -(2**15)
    I16_MAX: ClassVar[int] = 2**15 - 1
    HDG_CDEG_MIN: ClassVar[int] = 0
    HDG_CDEG_MAX: ClassVar[int] = 2**16 - 1
    BATTERY_REMAINING_MIN: ClassVar[int] = -1
    BATTERY_REMAINING_MAX: ClassVar[int] = 100
    U8_MIN: ClassVar[int] = 0
    U8_MAX: ClassVar[int] = 255
    COUNTER_MIN: ClassVar[int] = 0
    INTEGER_BOUNDS: ClassVar[Dict[str, Tuple[int, Optional[int]]]] = {
        SYSTEM_ID_FIELD: (SYSTEM_ID_MIN, SYSTEM_ID_MAX),
        LAT_E7_FIELD: (I32_MIN, I32_MAX),
        LON_E7_FIELD: (I32_MIN, I32_MAX),
        RELATIVE_ALT_MM_FIELD: (I32_MIN, I32_MAX),
        VX_CM_S_FIELD: (I16_MIN, I16_MAX),
        VY_CM_S_FIELD: (I16_MIN, I16_MAX),
        HDG_CDEG_FIELD: (HDG_CDEG_MIN, HDG_CDEG_MAX),
        BATTERY_REMAINING_FIELD: (BATTERY_REMAINING_MIN, BATTERY_REMAINING_MAX),
        BASE_MODE_FIELD: (U8_MIN, U8_MAX),
        SYSTEM_STATUS_FIELD: (U8_MIN, U8_MAX),
        RECEIVED_FIELD: (COUNTER_MIN, None),
        LOST_FIELD: (COUNTER_MIN, None),
        UPDATED_AT_US_FIELD: (COUNTER_MIN, None),
    }
    INTEGER_ERRORS: ClassVar[Dict[str, Type[Exception]]] = {
        SYSTEM_ID_FIELD: SEDroneSampleInvalidSystemId,
        LAT_E7_FIELD: SEDroneSampleInvalidLatE7,
        LON_E7_FIELD: SEDroneSampleInvalidLonE7,
        RELATIVE_ALT_MM_FIELD: SEDroneSampleInvalidRelativeAltMm,
        VX_CM_S_FIELD: SEDroneSampleInvalidVxCmS,
        VY_CM_S_FIELD: SEDroneSampleInvalidVyCmS,
        HDG_CDEG_FIELD: SEDroneSampleInvalidHdgCdeg,
        BATTERY_REMAINING_FIELD: SEDroneSampleInvalidBatteryRemaining,
        BASE_MODE_FIELD: SEDroneSampleInvalidBaseMode,
        SYSTEM_STATUS_FIELD: SEDroneSampleInvalidSystemStatus,
        RECEIVED_FIELD: SEDroneSampleInvalidReceived,
        LOST_FIELD: SEDroneSampleInvalidLost,
        UPDATED_AT_US_FIELD: SEDroneSampleInvalidUpdatedAtUs,
    }
    BEFORE: ClassVar[Literal["before"]] = "before"

    system_id: int = Field(description="The MAVLink system id of the Drone, from 1 to 255.")
    has_position: bool = Field(description="Whether the position fields hold a fix.")
    lat_e7: int = Field(description="The latitude in degrees times 10^7, a signed 32-bit integer.")
    lon_e7: int = Field(description="The longitude in degrees times 10^7, a signed 32-bit integer.")
    relative_alt_mm: int = Field(description="The altitude above the take-off point in millimetres, an i32.")
    vx_cm_s: int = Field(description="The ground speed to the north in centimetres per second, an i16.")
    vy_cm_s: int = Field(description="The ground speed to the east in centimetres per second, an i16.")
    hdg_cdeg: int = Field(description="The heading in centidegrees, an unsigned 16-bit integer.")
    battery_remaining: int = Field(description="The battery charge in percent, from 0 to 100, or -1 when unknown.")
    base_mode: int = Field(description="The MAVLink base mode bits, an unsigned 8-bit integer.")
    system_status: int = Field(description="The MAVLink system status, an unsigned 8-bit integer.")
    received: int = Field(description="The number of frames received from the Drone, 0 or more.")
    lost: int = Field(description="The number of frames lost, 0 or more.")
    updated_at_us: int = Field(description="When the sample was last updated, in microseconds, 0 or more.")

    @field_validator(
        SYSTEM_ID_FIELD,
        LAT_E7_FIELD,
        LON_E7_FIELD,
        RELATIVE_ALT_MM_FIELD,
        VX_CM_S_FIELD,
        VY_CM_S_FIELD,
        HDG_CDEG_FIELD,
        BATTERY_REMAINING_FIELD,
        BASE_MODE_FIELD,
        SYSTEM_STATUS_FIELD,
        RECEIVED_FIELD,
        LOST_FIELD,
        UPDATED_AT_US_FIELD,
        mode=BEFORE,
    )
    def validate_integers(cls, value: JsonValue, info: ValidationInfo) -> JsonValue:
        """Validate every integer field against the bounds of its type.

        Args:
            value (JsonValue): The raw input.
            info (ValidationInfo): The validation context, which names the field.

        Returns:
            JsonValue: The integer.

        Raises:
            Exception: The exception of the field, when the value is not an integer within its bounds.
        """
        name = str(info.field_name)
        minimum, maximum = cls.INTEGER_BOUNDS[name]
        return cls.parse_int(name, value, cls.INTEGER_ERRORS[name], minimum, maximum)

    @field_validator(HAS_POSITION_FIELD, mode=BEFORE)
    def validate_has_position(cls, value: JsonValue) -> JsonValue:
        """Validate ``has_position``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The flag.

        Raises:
            SEDroneSampleInvalidHasPosition: If the value is not a boolean.
        """
        if not isinstance(value, bool):
            raise SEDroneSampleInvalidHasPosition(f"Invalid {cls.HAS_POSITION_FIELD}: {value!r}. Must be a boolean.")
        return value
