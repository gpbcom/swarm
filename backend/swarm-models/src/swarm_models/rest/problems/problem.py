from __future__ import annotations

# Standard library imports
from typing import ClassVar, Literal, Optional

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_rest.models.problems.exceptions import (
    SEProblemInvalidDetail,
    SEProblemInvalidInstance,
    SEProblemInvalidStatus,
    SEProblemInvalidTitle,
    SEProblemInvalidType,
)


class Problem(BaseModel):
    """A problem document, as RFC 9457 defines it, answered as ``application/problem+json``.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the document.
        MEDIA_TYPE (ClassVar[str]): The media type of the document.
        TYPE_FIELD (ClassVar[str]): The name of the ``type`` field.
        TITLE_FIELD (ClassVar[str]): The name of the ``title`` field.
        STATUS_FIELD (ClassVar[str]): The name of the ``status`` field.
        DETAIL_FIELD (ClassVar[str]): The name of the ``detail`` field.
        INSTANCE_FIELD (ClassVar[str]): The name of the ``instance`` field.
        DEFAULT_TYPE (ClassVar[str]): The ``type`` of a problem with no more meaning than its status.
        STATUS_MIN (ClassVar[int]): The lowest status of an error.
        STATUS_MAX (ClassVar[int]): The highest status of an error.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        type (str): A URI reference that identifies the kind of problem.
        title (str): A short, human-readable summary of the kind of problem.
        status (int): The HTTP status of the answer.
        detail (Optional[str]): A human-readable explanation of this occurrence.
        instance (Optional[str]): A URI reference that identifies this occurrence.

    Notes:
        - ``None`` for ``detail`` and ``instance`` means the member is left out of the document.
        - A built problem never changes, so it can be shared between handlers.
    """

    MEDIA_TYPE: ClassVar[str] = "application/problem+json"
    TYPE_FIELD: ClassVar[str] = "type"
    TITLE_FIELD: ClassVar[str] = "title"
    STATUS_FIELD: ClassVar[str] = "status"
    DETAIL_FIELD: ClassVar[str] = "detail"
    INSTANCE_FIELD: ClassVar[str] = "instance"
    DEFAULT_TYPE: ClassVar[str] = "about:blank"
    STATUS_MIN: ClassVar[int] = 400
    STATUS_MAX: ClassVar[int] = 599
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", frozen=True)

    type: str = Field(default=DEFAULT_TYPE, description="A URI reference that identifies the kind of problem.")
    title: str = Field(description="A short, human-readable summary of the kind of problem.")
    status: int = Field(description="The HTTP status of the answer.")
    detail: Optional[str] = Field(default=None, description="A human-readable explanation of this occurrence.")
    instance: Optional[str] = Field(default=None, description="A URI reference that identifies this occurrence.")

    @field_validator(TYPE_FIELD, mode=BEFORE)
    def validate_type(cls, value: JsonValue) -> JsonValue:
        """Validate ``type``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped URI reference, or the default when ``None``.

        Raises:
            SEProblemInvalidType: If the value is not a non-empty string without whitespace.
        """
        if value is None:
            return cls.DEFAULT_TYPE
        if not isinstance(value, str) or not value.strip() or len(value.strip().split()) != 1:
            raise SEProblemInvalidType(f"Invalid type: {value!r}. Must be a non-empty string without whitespace.")
        return value.strip()

    @field_validator(TITLE_FIELD, mode=BEFORE)
    def validate_title(cls, value: JsonValue) -> JsonValue:
        """Validate ``title``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped title.

        Raises:
            SEProblemInvalidTitle: If the value is not a non-empty string.
        """
        if not isinstance(value, str) or not value.strip():
            raise SEProblemInvalidTitle(f"Invalid title: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(STATUS_FIELD, mode=BEFORE)
    def validate_status(cls, value: JsonValue) -> JsonValue:
        """Validate ``status``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The status.

        Raises:
            SEProblemInvalidStatus: If the value is not an integer from ``STATUS_MIN`` to ``STATUS_MAX``.
        """
        if isinstance(value, bool) or not isinstance(value, int) or not cls.STATUS_MIN <= value <= cls.STATUS_MAX:
            raise SEProblemInvalidStatus(
                f"Invalid status: {value!r}. Must be an integer in [{cls.STATUS_MIN}, {cls.STATUS_MAX}]."
            )
        return value

    @field_validator(DETAIL_FIELD, mode=BEFORE)
    def validate_detail(cls, value: JsonValue) -> JsonValue:
        """Validate ``detail``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped detail, or ``None``.

        Raises:
            SEProblemInvalidDetail: If the value is not a non-empty string.
        """
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise SEProblemInvalidDetail(f"Invalid detail: {value!r}. Must be a non-empty string.")
        return value.strip()

    @field_validator(INSTANCE_FIELD, mode=BEFORE)
    def validate_instance(cls, value: JsonValue) -> JsonValue:
        """Validate ``instance``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped URI reference, or ``None``.

        Raises:
            SEProblemInvalidInstance: If the value is not a non-empty string without whitespace.
        """
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip() or len(value.strip().split()) != 1:
            raise SEProblemInvalidInstance(
                f"Invalid instance: {value!r}. Must be a non-empty string without whitespace."
            )
        return value.strip()
