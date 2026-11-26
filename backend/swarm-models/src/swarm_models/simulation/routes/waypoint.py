from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.simulation.routes.exceptions import (
    SEWaypointInvalidAltitude,
    SEWaypointInvalidLat,
    SEWaypointInvalidLon,
)


class Waypoint(SwarmModel):
    """One point of a route.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the waypoint.
        lat_e7 (int): The latitude in degrees multiplied by 1e7.
        lon_e7 (int): The longitude in degrees multiplied by 1e7.
        altitude_m (float): The altitude, in metres.
        LAT_E7_FIELD (str): The name of the ``lat_e7`` field, for its validator.
        LON_E7_FIELD (str): The name of the ``lon_e7`` field, for its validator.
        ALTITUDE_FIELD (str): The name of the ``altitude_m`` field, for its validator.
        LAT_E7_MIN (int): The smallest accepted latitude.
        LAT_E7_MAX (int): The largest accepted latitude.
        LON_E7_MIN (int): The smallest accepted longitude.
        LON_E7_MAX (int): The largest accepted longitude.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - Latitude and longitude are integers, as in the shared telemetry frame.
        - **Booleans are refused wherever a number is expected.**
        - No field has a default, so ``None`` is refused.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    LAT_E7_FIELD: ClassVar[str] = "lat_e7"
    LON_E7_FIELD: ClassVar[str] = "lon_e7"
    ALTITUDE_FIELD: ClassVar[str] = "altitude_m"
    LAT_E7_MIN: ClassVar[int] = -900000000
    LAT_E7_MAX: ClassVar[int] = 900000000
    LON_E7_MIN: ClassVar[int] = -1800000000
    LON_E7_MAX: ClassVar[int] = 1800000000
    BEFORE: ClassVar[Literal["before"]] = "before"

    lat_e7: int = Field(description="The latitude in degrees multiplied by 1e7.")
    lon_e7: int = Field(description="The longitude in degrees multiplied by 1e7.")
    altitude_m: float = Field(description="The altitude, in metres.")

    ############################
    # Publicly Exposed Methods #
    ############################

    @field_validator(LAT_E7_FIELD, mode=BEFORE)
    def validate_lat_e7(cls, value: JsonValue) -> int:
        """Validate ``lat_e7``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SEWaypointInvalidLat: When the value is not an integer within its bounds.
        """
        return cls.parse_int(cls.LAT_E7_FIELD, value, SEWaypointInvalidLat, cls.LAT_E7_MIN, cls.LAT_E7_MAX)

    @field_validator(LON_E7_FIELD, mode=BEFORE)
    def validate_lon_e7(cls, value: JsonValue) -> int:
        """Validate ``lon_e7``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            int: The integer, within its bounds.

        Raises:
            SEWaypointInvalidLon: When the value is not an integer within its bounds.
        """
        return cls.parse_int(cls.LON_E7_FIELD, value, SEWaypointInvalidLon, cls.LON_E7_MIN, cls.LON_E7_MAX)

    @field_validator(ALTITUDE_FIELD, mode=BEFORE)
    def validate_altitude_m(cls, value: JsonValue) -> float:
        """Validate ``altitude_m``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            float: A finite number above zero.

        Raises:
            SEWaypointInvalidAltitude: When the value is not a finite number above zero.
        """
        altitude = cls.parse_float(cls.ALTITUDE_FIELD, value, SEWaypointInvalidAltitude)
        if altitude <= 0:
            raise SEWaypointInvalidAltitude(f"Invalid {cls.ALTITUDE_FIELD}: {value!r}. Must be above zero.")
        return altitude
