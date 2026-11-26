from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_live.models.config.exceptions import SELiveSessionConfigInvalidStatusInterval


class LiveSessionConfig(BaseModel):
    """The settings of one live session.

    Attributes:
        status_interval_s (float): How often the session yields its status, in seconds.
        STATUS_INTERVAL_FIELD (str): The name of the ``status_interval_s`` field, for its validator.
        DEFAULT_STATUS_INTERVAL_S (float): The default status interval.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - A boolean is refused where a number is expected.
    """

    STATUS_INTERVAL_FIELD: ClassVar[str] = "status_interval_s"
    DEFAULT_STATUS_INTERVAL_S: ClassVar[float] = 5.0
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    status_interval_s: float = Field(
        default=DEFAULT_STATUS_INTERVAL_S,
        description="How often the session yields its status, in seconds. Defaults to 5.",
    )

    @field_validator(STATUS_INTERVAL_FIELD, mode=BEFORE)
    def validate_status_interval_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``status_interval_s``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The duration, or the default when ``None``.

        Raises:
            SELiveSessionConfigInvalidStatusInterval: If the value is not a positive number.
        """
        if value is None:
            return cls.DEFAULT_STATUS_INTERVAL_S
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise SELiveSessionConfigInvalidStatusInterval(
                f"Invalid status_interval_s: {value!r}. Must be a positive number."
            )
        return value
