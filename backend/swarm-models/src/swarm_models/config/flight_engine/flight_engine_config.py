from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.config.app_config import AppConfig
from swarm_models.config.flight_engine.exceptions import (
    SEFlightEngineConfigInvalidDroneStatesCatalogPath,
    SEFlightEngineConfigInvalidLinkLostAfter,
    SEFlightEngineConfigInvalidLive,
    SEFlightEngineConfigInvalidMissionsCatalogPath,
    SEFlightEngineConfigInvalidNats,
    SEFlightEngineConfigInvalidStatusInterval,
    SEFlightEngineConfigInvalidTickInterval,
    SEFlightEngineConfigUnreadable,
)
from swarm_models.config.flight_engine.live_server_config import LiveServerConfig
from swarm_nats.models.config.nats_client_config import NatsClientConfig


class FlightEngineConfig(AppConfig):
    """The configuration of the flight engine app, loaded from ``conf/app.yaml``.

    Attributes:
        tick_interval_ms (int): The interval between two safety ticks of a Mission, in milliseconds.
        status_interval_s (float): How often the engine yields its status, in seconds.
        link_lost_after_ms (int): How long without a frame before a Drone counts as lost, in milliseconds.
        missions_catalog_path (str): The path of the Mission catalogue.
        drone_states_catalog_path (str): The path of the Drone state catalogue.
        nats (NatsClientConfig): The connection to NATS.
        live (LiveServerConfig): The live server.
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        TICK_INTERVAL_FIELD (str): The name of the ``tick_interval_ms`` field, for its validator.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field, for its validator.
        LINK_LOST_AFTER_FIELD (str): The name of the ``link_lost_after_ms`` field, for its validator.
        MISSIONS_CATALOG_PATH_FIELD (str): The name of the ``missions_catalog_path`` field, for its validator.
        DRONE_STATES_CATALOG_PATH_FIELD (str): The name of the ``drone_states_catalog_path`` field.
        NATS_FIELD (str): The name of the ``nats`` field, for its validator.
        LIVE_FIELD (str): The name of the ``live`` field, for its validator.
        DEFAULT_TICK_INTERVAL_MS (int): The default tick, 50 ms, which is 20 Hz.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        DEFAULT_LINK_LOST_AFTER_MS (int): The default delay of a Link-loss, 5 s.
        DEFAULT_MISSIONS_CATALOG_PATH (str): The default path of the Mission catalogue.
        DEFAULT_DRONE_STATES_CATALOG_PATH (str): The default path of the Drone state catalogue.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - Every duration is positive.
        - A relative catalogue path is read in the folder of the app, which ``AppConfig`` gives: ``SWARM_APP_ROOT`` in
          the image.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, validate_default=True)

    UNREADABLE: ClassVar[type[Exception]] = SEFlightEngineConfigUnreadable
    TICK_INTERVAL_FIELD: ClassVar[str] = "tick_interval_ms"
    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    LINK_LOST_AFTER_FIELD: ClassVar[str] = "link_lost_after_ms"
    MISSIONS_CATALOG_PATH_FIELD: ClassVar[str] = "missions_catalog_path"
    DRONE_STATES_CATALOG_PATH_FIELD: ClassVar[str] = "drone_states_catalog_path"
    NATS_FIELD: ClassVar[str] = "nats"
    LIVE_FIELD: ClassVar[str] = "live"
    DEFAULT_TICK_INTERVAL_MS: ClassVar[int] = 50
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    DEFAULT_LINK_LOST_AFTER_MS: ClassVar[int] = 5000
    DEFAULT_MISSIONS_CATALOG_PATH: ClassVar[str] = "conf/catalogs/missions.yaml"
    DEFAULT_DRONE_STATES_CATALOG_PATH: ClassVar[str] = "conf/catalogs/drone_states.yaml"
    BEFORE: ClassVar[Literal["before"]] = "before"

    tick_interval_ms: int = Field(
        default=DEFAULT_TICK_INTERVAL_MS,
        description="The interval between two safety ticks of a Mission, in milliseconds. Defaults to 50.",
    )
    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often the engine yields its status, in seconds. Defaults to 5.",
    )
    link_lost_after_ms: int = Field(
        default=DEFAULT_LINK_LOST_AFTER_MS,
        description="How long without a frame before a Drone counts as lost, in milliseconds. Defaults to 5000.",
    )
    missions_catalog_path: str = Field(
        default=DEFAULT_MISSIONS_CATALOG_PATH,
        description="The path of the Mission catalogue.",
    )
    drone_states_catalog_path: str = Field(
        default=DEFAULT_DRONE_STATES_CATALOG_PATH,
        description="The path of the Drone state catalogue.",
    )
    nats: NatsClientConfig = Field(default_factory=NatsClientConfig, description="The connection to NATS.")
    live: LiveServerConfig = Field(default_factory=LiveServerConfig, description="The live server.")

    @field_validator(TICK_INTERVAL_FIELD, mode=BEFORE)
    def validate_tick_interval_ms(cls, value: JsonValue) -> JsonValue:
        """Validate ``tick_interval_ms``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The interval, or the default when ``None``.

        Raises:
            SEFlightEngineConfigInvalidTickInterval: If the value is not a positive integer.
        """
        if value is None:
            return cls.DEFAULT_TICK_INTERVAL_MS
        return SwarmModel.parse_int(cls.TICK_INTERVAL_FIELD, value, SEFlightEngineConfigInvalidTickInterval, 1)

    @field_validator(STATUS_INTERVAL_FIELD, mode=BEFORE)
    def validate_status_interval_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``status_interval_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The interval, or the default when ``None``.

        Raises:
            SEFlightEngineConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        number = SwarmModel.parse_float(cls.STATUS_INTERVAL_FIELD, value, SEFlightEngineConfigInvalidStatusInterval)
        if number <= 0:
            raise SEFlightEngineConfigInvalidStatusInterval(
                f"Invalid {cls.STATUS_INTERVAL_FIELD}: {value!r}. Must be a positive number."
            )
        return number

    @field_validator(LINK_LOST_AFTER_FIELD, mode=BEFORE)
    def validate_link_lost_after_ms(cls, value: JsonValue) -> JsonValue:
        """Validate ``link_lost_after_ms``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The delay, or the default when ``None``.

        Raises:
            SEFlightEngineConfigInvalidLinkLostAfter: If the value is not a positive integer.
        """
        if value is None:
            return cls.DEFAULT_LINK_LOST_AFTER_MS
        return SwarmModel.parse_int(cls.LINK_LOST_AFTER_FIELD, value, SEFlightEngineConfigInvalidLinkLostAfter, 1)

    @field_validator(MISSIONS_CATALOG_PATH_FIELD, mode=BEFORE)
    def validate_missions_catalog_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``missions_catalog_path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or the default when ``None``.

        Raises:
            SEFlightEngineConfigInvalidMissionsCatalogPath: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_MISSIONS_CATALOG_PATH
        return SwarmModel.parse_text(
            cls.MISSIONS_CATALOG_PATH_FIELD, value, SEFlightEngineConfigInvalidMissionsCatalogPath
        )

    @field_validator(DRONE_STATES_CATALOG_PATH_FIELD, mode=BEFORE)
    def validate_drone_states_catalog_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``drone_states_catalog_path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or the default when ``None``.

        Raises:
            SEFlightEngineConfigInvalidDroneStatesCatalogPath: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_DRONE_STATES_CATALOG_PATH
        return SwarmModel.parse_text(
            cls.DRONE_STATES_CATALOG_PATH_FIELD, value, SEFlightEngineConfigInvalidDroneStatesCatalogPath
        )

    @field_validator(NATS_FIELD, mode=BEFORE)
    def validate_nats(cls, value: JsonValue) -> JsonValue:
        """Validate ``nats``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The section as a mapping, or an empty one when ``None``.

        Raises:
            SEFlightEngineConfigInvalidNats: If the value is not a mapping.
        """
        if value is None:
            return {}
        if isinstance(value, NatsClientConfig):
            return value
        if not isinstance(value, dict):
            raise SEFlightEngineConfigInvalidNats(f"Invalid nats: {value!r}. Must be a mapping.")
        return value

    @field_validator(LIVE_FIELD, mode=BEFORE)
    def validate_live(cls, value: JsonValue) -> JsonValue:
        """Validate ``live``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The section as a mapping, or an empty one when ``None``.

        Raises:
            SEFlightEngineConfigInvalidLive: If the value is not a mapping.
        """
        if value is None:
            return {}
        if isinstance(value, LiveServerConfig):
            return value
        if not isinstance(value, dict):
            raise SEFlightEngineConfigInvalidLive(f"Invalid live: {value!r}. Must be a mapping.")
        return value
