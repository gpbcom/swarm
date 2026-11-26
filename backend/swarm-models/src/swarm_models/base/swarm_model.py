from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime
from math import isfinite
from typing import ClassVar, Optional, Type
from uuid import UUID

# Third-party imports
from pydantic import BaseModel, ConfigDict, JsonValue


class SwarmModel(BaseModel):
    """The base of every model of the package.

    It forbids unknown keys and offers the parsers that validators share.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys.
        UUID_VERSION (ClassVar[int]): The version of the identifiers.

    Notes:
        - Each parser raises the exception class it is given, so that every model keeps its own exceptions.
        - **Booleans are refused wherever a number is expected**, because Python treats them as integers.
    """

    model_config = ConfigDict(extra="forbid")

    UUID_VERSION: ClassVar[int] = 7

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def parse_uuid7(cls, field: str, value: JsonValue, error: Type[Exception]) -> UUID:
        """Parse a version 7 UUID.

        Args:
            field (str): The name of the field, for the message.
            value (JsonValue): A UUID or its string form.
            error (Type[Exception]): The exception raised when the value is refused.

        Returns:
            UUID: The UUID.

        Raises:
            Exception: The given ``error`` when the value is not a version 7 UUID.
        """
        parsed: Optional[UUID] = None
        if isinstance(value, UUID):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = UUID(value)
            except ValueError:
                parsed = None
        if parsed is None or parsed.version != cls.UUID_VERSION:
            raise error(f"Invalid {field}: {value!r}. Must be a version 7 UUID.")
        return parsed

    @classmethod
    def parse_utc(cls, field: str, value: JsonValue, error: Type[Exception]) -> datetime:
        """Parse a moment with its time zone and return it in UTC.

        Args:
            field (str): The name of the field, for the message.
            value (JsonValue): A datetime or an ISO 8601 string, both with a time zone.
            error (Type[Exception]): The exception raised when the value is refused.

        Returns:
            datetime: The same instant, in UTC.

        Raises:
            Exception: The given ``error`` when the value has no time zone or is not a moment.
        """
        parsed: Optional[datetime] = None
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError:
                parsed = None
        if parsed is None or parsed.tzinfo is None or parsed.utcoffset() is None:
            raise error(f"Invalid {field}: {value!r}. Must be a date and time with a time zone.")
        return parsed.astimezone(UTC)

    @classmethod
    def parse_text(cls, field: str, value: JsonValue, error: Type[Exception]) -> str:
        """Parse a text, stripped, which must not be empty.

        Args:
            field (str): The name of the field, for the message.
            value (JsonValue): The raw value.
            error (Type[Exception]): The exception raised when the value is refused.

        Returns:
            str: The stripped text.

        Raises:
            Exception: The given ``error`` when the value is not a string or is empty.
        """
        if not isinstance(value, str) or not value.strip():
            raise error(f"Invalid {field}: {value!r}. Must be a non-empty string.")
        return value.strip()

    @classmethod
    def parse_int(
        cls,
        field: str,
        value: JsonValue,
        error: Type[Exception],
        minimum: Optional[int] = None,
        maximum: Optional[int] = None,
    ) -> int:
        """Parse an integer within optional bounds.

        Args:
            field (str): The name of the field, for the message.
            value (JsonValue): The raw value.
            error (Type[Exception]): The exception raised when the value is refused.
            minimum (Optional[int]): The smallest accepted value.
            maximum (Optional[int]): The largest accepted value.

        Returns:
            int: The integer.

        Raises:
            Exception: The given ``error`` when the value is not an integer or is out of bounds.
        """
        if isinstance(value, bool) or not isinstance(value, int):
            raise error(f"Invalid {field}: {value!r}. Must be an integer.")
        if (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
            raise error(f"Invalid {field}: {value!r}. Must be in [{minimum}, {maximum}], where None means no bound.")
        return value

    @classmethod
    def parse_float(
        cls,
        field: str,
        value: JsonValue,
        error: Type[Exception],
        minimum: Optional[float] = None,
        maximum: Optional[float] = None,
        maximum_exclusive: bool = False,
    ) -> float:
        """Parse a finite number within optional bounds.

        Args:
            field (str): The name of the field, for the message.
            value (JsonValue): The raw value, an integer or a float.
            error (Type[Exception]): The exception raised when the value is refused.
            minimum (Optional[float]): The smallest accepted value.
            maximum (Optional[float]): The largest accepted value.
            maximum_exclusive (bool): Whether the maximum itself is refused.

        Returns:
            float: The number as a float.

        Raises:
            Exception: The given ``error`` when the value is not a finite number or is out of bounds.
        """
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise error(f"Invalid {field}: {value!r}. Must be a finite number.")
        number = float(value)
        if not isfinite(number):
            raise error(f"Invalid {field}: {value!r}. Must be a finite number.")
        too_high = maximum is not None and (number >= maximum if maximum_exclusive else number > maximum)
        if (minimum is not None and number < minimum) or too_high:
            raise error(f"Invalid {field}: {value!r}. Must be in [{minimum}, {maximum}], where None means no bound.")
        return number
