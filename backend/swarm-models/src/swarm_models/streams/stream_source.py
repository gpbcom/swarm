from __future__ import annotations

# Standard library imports
from re import fullmatch
from typing import ClassVar, Literal, Optional

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.streams.exceptions import (
    SEStreamSourceInvalidDomain,
    SEStreamSourceInvalidFilterSubject,
    SEStreamSourceInvalidName,
)


class StreamSource(SwarmModel):
    """A stream that another stream copies its messages from.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the source.
        NAME_FIELD (ClassVar[str]): The name of the ``name`` field.
        DOMAIN_FIELD (ClassVar[str]): The name of the ``domain`` field.
        FILTER_SUBJECT_FIELD (ClassVar[str]): The name of the ``filter_subject`` field.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        TOKEN_PATTERN (ClassVar[str]): The shape of a stream name and of a JetStream domain.
        SUBJECT_PATTERN (ClassVar[str]): The shape of a subject filter, tokens separated by dots.
        name (str): The name of the stream to copy from.
        domain (Optional[str]): The JetStream domain of that stream, such as the one of an edge, or none.
        filter_subject (Optional[str]): Copies only the messages of this subject, or none for all of them.

    Notes:
        - **The source is frozen**, because a stream specification must not change once it is built.
        - A cell stream sources the stream of an edge through the JetStream domain of the edge.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    NAME_FIELD: ClassVar[str] = "name"
    DOMAIN_FIELD: ClassVar[str] = "domain"
    FILTER_SUBJECT_FIELD: ClassVar[str] = "filter_subject"
    BEFORE: ClassVar[Literal["before"]] = "before"
    TOKEN_PATTERN: ClassVar[str] = r"[A-Za-z0-9_-]+"
    SUBJECT_PATTERN: ClassVar[str] = r"[^\s.]+(\.[^\s.]+)*"

    name: str = Field(description="The name of the stream to copy from.")
    domain: Optional[str] = Field(default=None, description="The JetStream domain of that stream, or none.")
    filter_subject: Optional[str] = Field(
        default=None, description="Copies only the messages of this subject, or none for all of them."
    )

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The stripped name.

        Raises:
            SEStreamSourceInvalidName: When the value does not match ``TOKEN_PATTERN``.
        """
        text = cls.parse_text(cls.NAME_FIELD, value, SEStreamSourceInvalidName)
        if fullmatch(cls.TOKEN_PATTERN, text) is None:
            raise SEStreamSourceInvalidName(f"Invalid name: {value!r}. Must match {cls.TOKEN_PATTERN!r}.")
        return text

    @field_validator(DOMAIN_FIELD, mode=BEFORE)
    def validate_domain(cls, value: JsonValue) -> JsonValue:
        """Validate ``domain``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The stripped domain, or the default.

        Raises:
            SEStreamSourceInvalidDomain: When the value does not match ``TOKEN_PATTERN``.
        """
        if value is None:
            return cls.model_fields[cls.DOMAIN_FIELD].get_default(call_default_factory=True)
        text = cls.parse_text(cls.DOMAIN_FIELD, value, SEStreamSourceInvalidDomain)
        if fullmatch(cls.TOKEN_PATTERN, text) is None:
            raise SEStreamSourceInvalidDomain(f"Invalid domain: {value!r}. Must match {cls.TOKEN_PATTERN!r}.")
        return text

    @field_validator(FILTER_SUBJECT_FIELD, mode=BEFORE)
    def validate_filter_subject(cls, value: JsonValue) -> JsonValue:
        """Validate ``filter_subject``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The stripped subject filter, or the default.

        Raises:
            SEStreamSourceInvalidFilterSubject: When the value does not match ``SUBJECT_PATTERN``.
        """
        if value is None:
            return cls.model_fields[cls.FILTER_SUBJECT_FIELD].get_default(call_default_factory=True)
        text = cls.parse_text(cls.FILTER_SUBJECT_FIELD, value, SEStreamSourceInvalidFilterSubject)
        if fullmatch(cls.SUBJECT_PATTERN, text) is None:
            raise SEStreamSourceInvalidFilterSubject(
                f"Invalid filter_subject: {value!r}. Must match {cls.SUBJECT_PATTERN!r}."
            )
        return text
