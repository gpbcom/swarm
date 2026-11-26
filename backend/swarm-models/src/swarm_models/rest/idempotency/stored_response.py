from __future__ import annotations

# Standard library imports
import re
from typing import ClassVar, List, Literal, Pattern, Tuple, Union

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_rest.models.idempotency.exceptions import (
    SEStoredResponseInvalidBody,
    SEStoredResponseInvalidFingerprint,
    SEStoredResponseInvalidHeaders,
    SEStoredResponseInvalidStatus,
)


class StoredResponse(BaseModel):
    """The answer to a request, kept to replay it when the same ``Idempotency-Key`` comes back.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the response.
        FINGERPRINT_FIELD (ClassVar[str]): The name of the ``fingerprint`` field.
        STATUS_FIELD (ClassVar[str]): The name of the ``status`` field.
        HEADERS_FIELD (ClassVar[str]): The name of the ``headers`` field.
        BODY_FIELD (ClassVar[str]): The name of the ``body`` field.
        FINGERPRINT_PATTERN (ClassVar[Pattern[str]]): The shape of a fingerprint, 64 lower-case hexadecimal digits.
        STATUS_MIN (ClassVar[int]): The lowest HTTP status.
        STATUS_MAX (ClassVar[int]): The highest HTTP status.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        fingerprint (str): The SHA-256 digest of the request the answer belongs to.
        status (int): The HTTP status of the answer.
        headers (List[Tuple[str, str]]): The headers of the answer, as name and value pairs.
        body (bytes): The body of the answer.
    """

    FINGERPRINT_FIELD: ClassVar[str] = "fingerprint"
    STATUS_FIELD: ClassVar[str] = "status"
    HEADERS_FIELD: ClassVar[str] = "headers"
    BODY_FIELD: ClassVar[str] = "body"
    FINGERPRINT_PATTERN: ClassVar[Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
    STATUS_MIN: ClassVar[int] = 100
    STATUS_MAX: ClassVar[int] = 599
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True)

    fingerprint: str = Field(description="The SHA-256 digest of the request the answer belongs to.")
    status: int = Field(description="The HTTP status of the answer.")
    headers: List[Tuple[str, str]] = Field(
        default_factory=list, description="The headers of the answer, as name and value pairs."
    )
    body: bytes = Field(default=b"", description="The body of the answer.")

    @field_validator(FINGERPRINT_FIELD, mode=BEFORE)
    def validate_fingerprint(cls, value: JsonValue) -> JsonValue:
        """Validate ``fingerprint``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The fingerprint.

        Raises:
            SEStoredResponseInvalidFingerprint: If the value is not 64 lower-case hexadecimal digits.
        """
        if not isinstance(value, str) or not cls.FINGERPRINT_PATTERN.match(value):
            raise SEStoredResponseInvalidFingerprint(
                f"Invalid fingerprint: {value!r}. Must be 64 lower-case hexadecimal digits."
            )
        return value

    @field_validator(STATUS_FIELD, mode=BEFORE)
    def validate_status(cls, value: JsonValue) -> JsonValue:
        """Validate ``status``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The status.

        Raises:
            SEStoredResponseInvalidStatus: If the value is not an integer from ``STATUS_MIN`` to ``STATUS_MAX``.
        """
        if isinstance(value, bool) or not isinstance(value, int) or not cls.STATUS_MIN <= value <= cls.STATUS_MAX:
            raise SEStoredResponseInvalidStatus(
                f"Invalid status: {value!r}. Must be an integer in [{cls.STATUS_MIN}, {cls.STATUS_MAX}]."
            )
        return value

    @field_validator(HEADERS_FIELD, mode=BEFORE)
    def validate_headers(cls, value: JsonValue) -> JsonValue:
        """Validate ``headers``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The headers as a list of pairs, or an empty list when ``None``.

        Raises:
            SEStoredResponseInvalidHeaders: If the value is not a list of pairs of a non-empty name and a value.
        """
        if value is None:
            return []
        if not isinstance(value, (list, tuple)):
            raise SEStoredResponseInvalidHeaders(f"Invalid headers: {value!r}. Must be a list of name and value pairs.")
        pairs: List[JsonValue] = []
        for pair in value:
            if (
                not isinstance(pair, (list, tuple))
                or len(pair) != 2
                or not isinstance(pair[0], str)
                or not pair[0].strip()
                or not isinstance(pair[1], str)
            ):
                raise SEStoredResponseInvalidHeaders(
                    f"Invalid headers: {value!r}. Each header must be a pair of a non-empty name and a value."
                )
            pairs.append([pair[0], pair[1]])
        return pairs

    @field_validator(BODY_FIELD, mode=BEFORE)
    def validate_body(cls, value: JsonValue) -> Union[JsonValue, bytes]:
        """Validate ``body``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            Union[JsonValue, bytes]: The body, or empty bytes when ``None``.

        Raises:
            SEStoredResponseInvalidBody: If the value is not bytes.
        """
        if value is None:
            return b""
        if not isinstance(value, bytes):
            raise SEStoredResponseInvalidBody(f"Invalid body: {value!r}. Must be bytes.")
        return value
