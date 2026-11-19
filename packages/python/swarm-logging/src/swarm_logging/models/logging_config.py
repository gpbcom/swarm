from __future__ import annotations

# Standard library imports
from typing import Optional

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_logging.models.enums import LogFormat
from swarm_logging.models.exceptions import SELoggingConfigInvalidFormat, SELoggingConfigInvalidPath


class LoggingConfig(BaseModel):
    """The settings that choose how logging is configured.

    Attributes:
        path (Optional[str]): The logging configuration file, or ``None`` for the built-in one.
        format (LogFormat): How a log record is written.
    """

    model_config = ConfigDict(extra="forbid", validate_default=True, frozen=True)

    path: Optional[str] = Field(default=None, description="The logging configuration file, or none for the default.")
    format: LogFormat = Field(default=LogFormat.COLOURED, description="How a log record is written.")

    @field_validator("path", mode="before")
    def validate_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or ``None``.

        Raises:
            SELoggingConfigInvalidPath: If the value is not a non-empty string.
        """
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise SELoggingConfigInvalidPath(f"Invalid path: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator("format", mode="before")
    def validate_format(cls, value: JsonValue) -> JsonValue:
        """Validate ``format``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The value of the format.

        Raises:
            SELoggingConfigInvalidFormat: If the value is not a log format or its value.
        """
        if value is None:
            return cls.model_fields["format"].get_default(call_default_factory=True)
        if isinstance(value, LogFormat):
            return value
        if isinstance(value, str) and value in {member.value for member in LogFormat}:
            return LogFormat(value)
        raise SELoggingConfigInvalidFormat(
            f"Invalid format: {value!r}. Must be one of {[member.value for member in LogFormat]}."
        )
