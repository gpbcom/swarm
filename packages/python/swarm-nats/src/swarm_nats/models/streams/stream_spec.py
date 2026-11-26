from __future__ import annotations

# Standard library imports
from re import fullmatch
from typing import ClassVar, List, Literal, Mapping, Sequence, Union

# Third-party imports
from pydantic import ConfigDict, Field, JsonValue, field_validator, model_validator

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_nats.models.enums import StreamRetention, StreamStorage
from swarm_nats.models.streams.exceptions import (
    SEStreamSpecInvalidDuplicateWindow,
    SEStreamSpecInvalidName,
    SEStreamSpecInvalidReplicas,
    SEStreamSpecInvalidRetention,
    SEStreamSpecInvalidSources,
    SEStreamSpecInvalidStorage,
    SEStreamSpecInvalidSubjects,
    SEStreamSpecNoSubjectsNorSources,
)
from swarm_nats.models.streams.stream_source import StreamSource


class StreamSpec(SwarmModel):
    """The specification of a JetStream stream.

    Attributes:
        model_config (ConfigDict): Forbids unknown keys and freezes the specification.
        NAME_FIELD (ClassVar[str]): The name of the ``name`` field.
        SUBJECTS_FIELD (ClassVar[str]): The name of the ``subjects`` field.
        REPLICAS_FIELD (ClassVar[str]): The name of the ``replicas`` field.
        STORAGE_FIELD (ClassVar[str]): The name of the ``storage`` field.
        RETENTION_FIELD (ClassVar[str]): The name of the ``retention`` field.
        DUPLICATE_WINDOW_FIELD (ClassVar[str]): The name of the ``duplicate_window_s`` field.
        SOURCES_FIELD (ClassVar[str]): The name of the ``sources`` field.
        BEFORE (ClassVar[Literal["before"]]): The mode of the validators.
        AFTER (ClassVar[Literal["after"]]): The mode of the cross-field validator.
        NAME_PATTERN (ClassVar[str]): The shape of a stream name.
        SUBJECT_PATTERN (ClassVar[str]): The shape of a subject filter, tokens separated by dots.
        REPLICAS_MIN (ClassVar[int]): The fewest replicas.
        REPLICAS_MAX (ClassVar[int]): The most replicas.
        name (str): The name of the stream.
        subjects (List[str]): The subjects the stream stores.
        replicas (int): How many servers of the cell keep a copy, three by default.
        storage (StreamStorage): Where the messages are kept.
        retention (StreamRetention): When the messages are removed.
        duplicate_window_s (float): The window, in seconds, in which a repeated message identifier is dropped.
        sources (List[StreamSource]): The streams this one copies, such as the stream of an edge.

    Notes:
        - **The specification is frozen**, because a stream is created from it once.
        - Streams are replicated three times inside the cell.
        - A stream has subjects, sources or both, and never neither.
        - A source given as a mapping becomes a ``StreamSource``, and its errors are raised unchanged.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    NAME_FIELD: ClassVar[str] = "name"
    SUBJECTS_FIELD: ClassVar[str] = "subjects"
    REPLICAS_FIELD: ClassVar[str] = "replicas"
    STORAGE_FIELD: ClassVar[str] = "storage"
    RETENTION_FIELD: ClassVar[str] = "retention"
    DUPLICATE_WINDOW_FIELD: ClassVar[str] = "duplicate_window_s"
    SOURCES_FIELD: ClassVar[str] = "sources"
    BEFORE: ClassVar[Literal["before"]] = "before"
    AFTER: ClassVar[Literal["after"]] = "after"
    NAME_PATTERN: ClassVar[str] = r"[A-Za-z0-9_-]+"
    SUBJECT_PATTERN: ClassVar[str] = r"[^\s.]+(\.[^\s.]+)*"
    REPLICAS_MIN: ClassVar[int] = 1
    REPLICAS_MAX: ClassVar[int] = 5

    name: str = Field(description="The name of the stream.")
    subjects: List[str] = Field(default_factory=list, description="The subjects the stream stores.")
    replicas: int = Field(default=3, description="How many servers of the cell keep a copy.")
    storage: StreamStorage = Field(default=StreamStorage.FILE, description="Where the messages are kept.")
    retention: StreamRetention = Field(default=StreamRetention.LIMITS, description="When the messages are removed.")
    duplicate_window_s: float = Field(
        default=120.0, description="The window, in seconds, in which a repeated message identifier is dropped."
    )
    sources: List[StreamSource] = Field(default_factory=list, description="The streams this one copies.")

    @field_validator(NAME_FIELD, mode=BEFORE)
    def validate_name(cls, value: JsonValue) -> JsonValue:
        """Validate ``name``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The stripped name.

        Raises:
            SEStreamSpecInvalidName: When the value does not match ``NAME_PATTERN``.
        """
        text = cls.parse_text(cls.NAME_FIELD, value, SEStreamSpecInvalidName)
        if fullmatch(cls.NAME_PATTERN, text) is None:
            raise SEStreamSpecInvalidName(f"Invalid name: {value!r}. Must match {cls.NAME_PATTERN!r}.")
        return text

    @field_validator(SUBJECTS_FIELD, mode=BEFORE)
    def validate_subjects(cls, value: JsonValue) -> JsonValue:
        """Validate ``subjects``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The stripped subjects, or the default.

        Raises:
            SEStreamSpecInvalidSubjects: When the value is not a list of subjects matching ``SUBJECT_PATTERN``.
        """
        if value is None:
            return cls.model_fields[cls.SUBJECTS_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, (list, tuple)):
            raise SEStreamSpecInvalidSubjects(f"Invalid subjects: {value!r}. Must be a list of subjects.")
        subjects: List[JsonValue] = []
        for item in value:
            text = cls.parse_text(cls.SUBJECTS_FIELD, item, SEStreamSpecInvalidSubjects)
            if fullmatch(cls.SUBJECT_PATTERN, text) is None:
                raise SEStreamSpecInvalidSubjects(f"Invalid subjects: {item!r}. Must match {cls.SUBJECT_PATTERN!r}.")
            subjects.append(text)
        return subjects

    @field_validator(REPLICAS_FIELD, mode=BEFORE)
    def validate_replicas(cls, value: JsonValue) -> JsonValue:
        """Validate ``replicas``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The number of replicas, or the default.

        Raises:
            SEStreamSpecInvalidReplicas: When the value is not an integer within the bounds.
        """
        if value is None:
            return cls.model_fields[cls.REPLICAS_FIELD].get_default(call_default_factory=True)
        return cls.parse_int(
            cls.REPLICAS_FIELD, value, SEStreamSpecInvalidReplicas, minimum=cls.REPLICAS_MIN, maximum=cls.REPLICAS_MAX
        )

    @field_validator(STORAGE_FIELD, mode=BEFORE)
    def validate_storage(cls, value: JsonValue) -> JsonValue:
        """Validate ``storage``.

        Args:
            value (JsonValue): A ``StreamStorage`` or its value.

        Returns:
            JsonValue: The storage, or the default.

        Raises:
            SEStreamSpecInvalidStorage: When the value is not a ``StreamStorage``.
        """
        if value is None:
            return cls.model_fields[cls.STORAGE_FIELD].get_default(call_default_factory=True)
        members = [member.value for member in StreamStorage]
        if not isinstance(value, str) or value not in members:
            raise SEStreamSpecInvalidStorage(f"Invalid storage: {value!r}. Must be one of {members}.")
        return StreamStorage(value)

    @field_validator(RETENTION_FIELD, mode=BEFORE)
    def validate_retention(cls, value: JsonValue) -> JsonValue:
        """Validate ``retention``.

        Args:
            value (JsonValue): A ``StreamRetention`` or its value.

        Returns:
            JsonValue: The retention, or the default.

        Raises:
            SEStreamSpecInvalidRetention: When the value is not a ``StreamRetention``.
        """
        if value is None:
            return cls.model_fields[cls.RETENTION_FIELD].get_default(call_default_factory=True)
        members = [member.value for member in StreamRetention]
        if not isinstance(value, str) or value not in members:
            raise SEStreamSpecInvalidRetention(f"Invalid retention: {value!r}. Must be one of {members}.")
        return StreamRetention(value)

    @field_validator(DUPLICATE_WINDOW_FIELD, mode=BEFORE)
    def validate_duplicate_window_s(cls, value: JsonValue) -> JsonValue:
        """Validate ``duplicate_window_s``.

        Args:
            value (JsonValue): The raw value.

        Returns:
            JsonValue: The window in seconds, or the default.

        Raises:
            SEStreamSpecInvalidDuplicateWindow: When the value is not a finite number above zero.
        """
        if value is None:
            return cls.model_fields[cls.DUPLICATE_WINDOW_FIELD].get_default(call_default_factory=True)
        window = cls.parse_float(cls.DUPLICATE_WINDOW_FIELD, value, SEStreamSpecInvalidDuplicateWindow, minimum=0.0)
        if window == 0.0:
            raise SEStreamSpecInvalidDuplicateWindow(
                f"Invalid duplicate_window_s: {value!r}. Must be a finite number greater than 0."
            )
        return window

    @field_validator(SOURCES_FIELD, mode=BEFORE)
    def validate_sources(cls, value: JsonValue) -> Union[List[StreamSource], JsonValue]:
        """Validate ``sources``.

        Args:
            value (JsonValue): A list of ``StreamSource`` or of mappings.

        Returns:
            Union[List[StreamSource], JsonValue]: The sources, or the default.

        Raises:
            SEStreamSpecInvalidSources: When the value is not a list of sources or mappings.
        """
        if value is None:
            return cls.model_fields[cls.SOURCES_FIELD].get_default(call_default_factory=True)
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise SEStreamSpecInvalidSources(f"Invalid sources: {value!r}. Must be a list of stream sources.")
        sources: List[StreamSource] = []
        for item in value:
            if isinstance(item, StreamSource):
                sources.append(item)
            elif isinstance(item, Mapping):
                sources.append(StreamSource.model_validate(dict(item)))
            else:
                raise SEStreamSpecInvalidSources(f"Invalid sources: {item!r}. Must be a stream source or a mapping.")
        return sources

    @model_validator(mode=AFTER)
    def validate_subjects_or_sources(self) -> StreamSpec:
        """Check that the stream has subjects or sources.

        Returns:
            StreamSpec: The specification.

        Raises:
            SEStreamSpecNoSubjectsNorSources: When both ``subjects`` and ``sources`` are empty.
        """
        if not self.subjects and not self.sources:
            raise SEStreamSpecNoSubjectsNorSources(
                f"Invalid stream: {self.name!r}. Must have at least one subject or one source."
            )
        return self
