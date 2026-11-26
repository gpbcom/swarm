from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, Literal, Type

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, ValidationInfo, field_validator

# First-party imports
from simulator.models.config.exceptions import (
    SEFlightConfigInvalidArmTimeout,
    SEFlightConfigInvalidHeartbeatTimeout,
    SEFlightConfigInvalidRouteTimeout,
    SEFlightConfigInvalidStatusInterval,
    SEInvalidFlightConfigException,
)


class FlightConfig(BaseModel):
    """The timings of a flight.

    Attributes:
        heartbeat_timeout_s (float): How long to wait for a heartbeat of the drone, in seconds.
        arm_timeout_s (float): How long to wait for the drone to arm, in seconds.
        route_timeout_s (float): How long a route may last, in seconds.
        status_interval_s (float): How often a flight yields its status, in seconds.
        HEARTBEAT_FIELD (str): The name of the ``heartbeat_timeout_s`` field.
        ARM_FIELD (str): The name of the ``arm_timeout_s`` field.
        ROUTE_FIELD (str): The name of the ``route_timeout_s`` field.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field.
        DEFAULT_HEARTBEAT_TIMEOUT_S (float): The default heartbeat timeout.
        DEFAULT_ARM_TIMEOUT_S (float): The default arm timeout.
        DEFAULT_ROUTE_TIMEOUT_S (float): The default route timeout.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        ERRORS (Dict[str, Type[SEInvalidFlightConfigException]]): The exception of each field.
        DEFAULTS (Dict[str, float]): The default of each field.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - The four timings share one validator, because they share one rule: a positive number.
        - A boolean is refused where a number is expected.
    """

    HEARTBEAT_FIELD: ClassVar[str] = "heartbeat_timeout_s"
    ARM_FIELD: ClassVar[str] = "arm_timeout_s"
    ROUTE_FIELD: ClassVar[str] = "route_timeout_s"
    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    DEFAULT_HEARTBEAT_TIMEOUT_S: ClassVar[float] = 30.0
    DEFAULT_ARM_TIMEOUT_S: ClassVar[float] = 120.0
    DEFAULT_ROUTE_TIMEOUT_S: ClassVar[float] = 600.0
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    ERRORS: ClassVar[Dict[str, Type[SEInvalidFlightConfigException]]] = {
        HEARTBEAT_FIELD: SEFlightConfigInvalidHeartbeatTimeout,
        ARM_FIELD: SEFlightConfigInvalidArmTimeout,
        ROUTE_FIELD: SEFlightConfigInvalidRouteTimeout,
        STATUS_INTERVAL_FIELD: SEFlightConfigInvalidStatusInterval,
    }
    DEFAULTS: ClassVar[Dict[str, float]] = {
        HEARTBEAT_FIELD: DEFAULT_HEARTBEAT_TIMEOUT_S,
        ARM_FIELD: DEFAULT_ARM_TIMEOUT_S,
        ROUTE_FIELD: DEFAULT_ROUTE_TIMEOUT_S,
        STATUS_INTERVAL_FIELD: DEFAULT_STATUS_INTERVAL_S,
    }
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    heartbeat_timeout_s: float = Field(
        default=DEFAULT_HEARTBEAT_TIMEOUT_S,
        description="How long to wait for a heartbeat of the drone, in seconds. Defaults to 30.",
    )
    arm_timeout_s: float = Field(
        default=DEFAULT_ARM_TIMEOUT_S,
        description="How long to wait for the drone to arm, in seconds. Defaults to 120.",
    )
    route_timeout_s: float = Field(
        default=DEFAULT_ROUTE_TIMEOUT_S,
        description="How long a route may last, in seconds. Defaults to 600.",
    )
    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often a flight yields its status, in seconds. Defaults to 5.",
    )

    @field_validator(HEARTBEAT_FIELD, ARM_FIELD, ROUTE_FIELD, STATUS_INTERVAL_FIELD, mode=BEFORE)
    def validate_timing(cls, value: JsonValue, info: ValidationInfo) -> JsonValue:
        """Validate one of the four timings.

        Args:
            value (JsonValue): The raw input.
            info (ValidationInfo): The field being validated.

        Returns:
            JsonValue: The duration, or the default of the field when ``None``.

        Raises:
            SEInvalidFlightConfigException: The exception of the field, if the value is not a positive number.
        """
        name = str(info.field_name)
        if value is None:
            return cls.DEFAULTS[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise cls.ERRORS[name](f"Invalid {name}: {value!r}. Must be a positive number.")
        return value
