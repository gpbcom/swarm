from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.config.simulator.exceptions import SERouteConfigInvalidAltitude, SERouteConfigInvalidSide


class RouteConfig(BaseModel):
    """The shape of the square route the simulator flies.

    Attributes:
        side_m (float): The side of the square, in metres.
        altitude_m (float): The altitude of the route, in metres.
        SIDE_FIELD (str): The name of the ``side_m`` field, for its validator.
        ALTITUDE_FIELD (str): The name of the ``altitude_m`` field, for its validator.
        DEFAULT_SIDE_M (float): The default side.
        DEFAULT_ALTITUDE_M (float): The default altitude.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - A boolean is refused where a number is expected.
    """

    SIDE_FIELD: ClassVar[str] = "side_m"
    ALTITUDE_FIELD: ClassVar[str] = "altitude_m"
    DEFAULT_SIDE_M: ClassVar[float] = 50.0
    DEFAULT_ALTITUDE_M: ClassVar[float] = 20.0
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    side_m: float = Field(default=DEFAULT_SIDE_M, description="The side of the square route, in metres.")
    altitude_m: float = Field(default=DEFAULT_ALTITUDE_M, description="The altitude of the route, in metres.")

    @field_validator(SIDE_FIELD, mode=BEFORE)
    def validate_side_m(cls, value: JsonValue) -> JsonValue:
        """Validate ``side_m``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The length, or the default when ``None``.

        Raises:
            SERouteConfigInvalidSide: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_SIDE_M
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SERouteConfigInvalidSide(f"Invalid side_m: {value!r}. Must be a positive number.")
        return value

    @field_validator(ALTITUDE_FIELD, mode=BEFORE)
    def validate_altitude_m(cls, value: JsonValue) -> JsonValue:
        """Validate ``altitude_m``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The altitude, or the default when ``None``.

        Raises:
            SERouteConfigInvalidAltitude: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_ALTITUDE_M
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SERouteConfigInvalidAltitude(f"Invalid altitude_m: {value!r}. Must be a positive number.")
        return value
