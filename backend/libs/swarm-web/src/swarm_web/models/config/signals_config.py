from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Optional, Set
from urllib.parse import urlparse

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_web.models.config.exceptions import (
    SESignalsConfigInvalidCell,
    SESignalsConfigInvalidEnabled,
    SESignalsConfigInvalidEndpoint,
    SESignalsConfigInvalidMetricsInterval,
    SESignalsConfigInvalidRedactionsPath,
    SESignalsConfigInvalidServiceName,
)


class SignalsConfig(BaseModel):
    """The settings of the signals (traces, metrics and logs) a process exports.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys, validates the defaults and freezes the configuration.
        ENABLED_FIELD (ClassVar[str]): The name of the ``enabled`` field.
        ENDPOINT_FIELD (ClassVar[str]): The name of the ``endpoint`` field.
        SERVICE_NAME_FIELD (ClassVar[str]): The name of the ``service_name`` field.
        CELL_FIELD (ClassVar[str]): The name of the ``cell`` field.
        METRICS_INTERVAL_FIELD (ClassVar[str]): The name of the ``metrics_interval_s`` field.
        REDACTIONS_PATH_FIELD (ClassVar[str]): The name of the ``redactions_path`` field.
        DEFAULT_ENABLED (ClassVar[bool]): Signals are not exported by default.
        DEFAULT_ENDPOINT (ClassVar[str]): The default OTLP/HTTP collector.
        DEFAULT_SERVICE_NAME (ClassVar[str]): The default service name.
        DEFAULT_CELL (ClassVar[str]): The default cell.
        DEFAULT_METRICS_INTERVAL_S (ClassVar[float]): The default export interval of metrics, in seconds.
        ENDPOINT_SCHEMES (ClassVar[Set[str]]): The URL schemes an endpoint may use.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        enabled (bool): Whether the process exports its signals.
        endpoint (str): The OTLP/HTTP endpoint of the collector.
        service_name (str): The service name of the signals.
        cell (str): The cell that emits the signals.
        metrics_interval_s (float): The export interval of metrics, in seconds.
        redactions_path (Optional[str]): The redaction catalogue, or None for the reference one.
    """

    ENABLED_FIELD: ClassVar[str] = "enabled"
    ENDPOINT_FIELD: ClassVar[str] = "endpoint"
    SERVICE_NAME_FIELD: ClassVar[str] = "service_name"
    CELL_FIELD: ClassVar[str] = "cell"
    METRICS_INTERVAL_FIELD: ClassVar[str] = "metrics_interval_s"
    REDACTIONS_PATH_FIELD: ClassVar[str] = "redactions_path"
    DEFAULT_ENABLED: ClassVar[bool] = False
    DEFAULT_ENDPOINT: ClassVar[str] = "http://otel-collector:4318"
    DEFAULT_SERVICE_NAME: ClassVar[str] = "swarm"
    DEFAULT_CELL: ClassVar[str] = "local"
    DEFAULT_METRICS_INTERVAL_S: ClassVar[float] = 60.0
    ENDPOINT_SCHEMES: ClassVar[Set[str]] = {"http", "https"}
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True, frozen=True)

    enabled: bool = Field(default=DEFAULT_ENABLED, description="Whether the process exports its signals.")
    endpoint: str = Field(default=DEFAULT_ENDPOINT, description="The OTLP/HTTP endpoint of the collector.")
    service_name: str = Field(default=DEFAULT_SERVICE_NAME, description="The service name of the signals.")
    cell: str = Field(default=DEFAULT_CELL, description="The cell that emits the signals.")
    metrics_interval_s: float = Field(
        default=DEFAULT_METRICS_INTERVAL_S, description="The export interval of metrics, in seconds."
    )
    redactions_path: Optional[str] = Field(
        default=None, description="The redaction catalogue, or None for the reference one."
    )

    @field_validator(ENABLED_FIELD, mode=BEFORE)
    def validate_enabled(cls, value: JsonValue) -> JsonValue:
        """Validate ``enabled``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The flag, or the default when ``None``.

        Raises:
            SESignalsConfigInvalidEnabled: If the value is not a boolean.
        """
        if value is None:
            return cls.DEFAULT_ENABLED
        if not isinstance(value, bool):
            raise SESignalsConfigInvalidEnabled(f"Invalid enabled: {value!r}. Must be a boolean.")
        return value

    @field_validator(ENDPOINT_FIELD, mode=BEFORE)
    def validate_endpoint(cls, value: JsonValue) -> JsonValue:
        """Validate ``endpoint``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped endpoint, or the default when ``None``.

        Raises:
            SESignalsConfigInvalidEndpoint: If the value is not an ``http`` or ``https`` URL with a host.
        """
        if value is None:
            return cls.DEFAULT_ENDPOINT
        if not isinstance(value, str):
            raise SESignalsConfigInvalidEndpoint(f"Invalid endpoint: {value!r}. Must be an http or https URL.")
        stripped = value.strip()
        parsed = urlparse(stripped)
        if parsed.scheme not in cls.ENDPOINT_SCHEMES or not parsed.netloc:
            raise SESignalsConfigInvalidEndpoint(f"Invalid endpoint: {value!r}. Must be an http or https URL.")
        return stripped

    @field_validator(SERVICE_NAME_FIELD, mode=BEFORE)
    def validate_service_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``service_name``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped name, or the default when ``None``.

        Raises:
            SESignalsConfigInvalidServiceName: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_SERVICE_NAME
        if not isinstance(value, str) or not value.strip():
            raise SESignalsConfigInvalidServiceName(f"Invalid service_name: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(CELL_FIELD, mode=BEFORE)
    def validate_cell(cls, value: JsonValue) -> JsonValue:
        """Validate ``cell``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped cell, or the default when ``None``.

        Raises:
            SESignalsConfigInvalidCell: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_CELL
        if not isinstance(value, str) or not value.strip():
            raise SESignalsConfigInvalidCell(f"Invalid cell: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(METRICS_INTERVAL_FIELD, mode=BEFORE)
    def validate_metrics_interval_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``metrics_interval_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SESignalsConfigInvalidMetricsInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_METRICS_INTERVAL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SESignalsConfigInvalidMetricsInterval(
                f"Invalid metrics_interval_s: {value!r}. Must be a positive number."
            )
        return value

    @field_validator(REDACTIONS_PATH_FIELD, mode=BEFORE)
    def validate_redactions_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``redactions_path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or ``None`` for the reference catalogue.

        Raises:
            SESignalsConfigInvalidRedactionsPath: If the value is not a non-empty string.
        """
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise SESignalsConfigInvalidRedactionsPath(
                f"Invalid redactions_path: {value!r}. Must be a non-empty string."
            )
        return value.strip()
