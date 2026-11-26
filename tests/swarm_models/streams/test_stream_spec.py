from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import StreamRetention, StreamStorage
from swarm_models.streams.exceptions import (
    SEInvalidStreamSpecException,
    SEStreamSourceInvalidName,
    SEStreamSpecInvalidDuplicateWindow,
    SEStreamSpecInvalidName,
    SEStreamSpecInvalidReplicas,
    SEStreamSpecInvalidRetention,
    SEStreamSpecInvalidSources,
    SEStreamSpecInvalidStorage,
    SEStreamSpecInvalidSubjects,
    SEStreamSpecNoSubjectsNorSources,
)
from swarm_models.streams.stream_source import StreamSource
from swarm_models.streams.stream_spec import StreamSpec


class TestStreamSpec:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "name": "EVENTS",
        "subjects": ["op.*.fleet.>", "op.*.mission.*.>"],
        "replicas": 3,
        "storage": "file",
        "retention": "limits",
        "duplicate_window_s": 120.0,
        "sources": [{"name": "EDGE_EVENTS", "domain": "edge-1"}],
    }
    BAD_SOURCES: ClassVar[List[JsonValue]] = [{"name": "a b"}]

    def build(self, **changes: JsonValue) -> StreamSpec:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return StreamSpec.model_validate(values)

    def test_defaults(self) -> None:
        spec = StreamSpec(name="EVENTS", subjects=["op.*.fleet.>"])
        assert spec.subjects == ["op.*.fleet.>"]
        assert spec.replicas == 3
        assert spec.storage == StreamStorage.FILE
        assert spec.retention == StreamRetention.LIMITS
        assert spec.duplicate_window_s == 120.0
        assert spec.sources == []

    def test_streams_are_replicated_three_times_by_default(self) -> None:
        assert StreamSpec(name="EVENTS", subjects=["op.*.fleet.>"]).replicas == 3

    def test_full_valid_construction(self) -> None:
        spec = StreamSpec(
            name="EVENTS",
            subjects=["op.*.fleet.>"],
            replicas=5,
            storage=StreamStorage.MEMORY,
            retention=StreamRetention.WORK_QUEUE,
            duplicate_window_s=30.5,
            sources=[StreamSource(name="EDGE_EVENTS", domain="edge-1", filter_subject="op.*.fleet.>")],
        )
        assert spec.name == "EVENTS"
        assert spec.replicas == 5
        assert spec.storage == StreamStorage.MEMORY
        assert spec.retention == StreamRetention.WORK_QUEUE
        assert spec.duplicate_window_s == 30.5
        assert spec.sources[0].domain == "edge-1"

    @pytest.mark.parametrize(
        ("name", "default"),
        [
            ("subjects", []),
            ("replicas", 3),
            ("storage", StreamStorage.FILE),
            ("retention", StreamRetention.LIMITS),
            ("duplicate_window_s", 120.0),
            ("sources", []),
        ],
    )
    def test_none_becomes_the_default(self, name: str, default: JsonValue) -> None:
        assert getattr(self.build(**{name: None}), name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("name", None, SEStreamSpecInvalidName),
            ("name", "", SEStreamSpecInvalidName),
            ("name", "a b", SEStreamSpecInvalidName),
            ("name", "a.b", SEStreamSpecInvalidName),
            ("name", 3, SEStreamSpecInvalidName),
            ("subjects", "op.>", SEStreamSpecInvalidSubjects),
            ("subjects", 3, SEStreamSpecInvalidSubjects),
            ("subjects", [""], SEStreamSpecInvalidSubjects),
            ("subjects", ["op. fleet"], SEStreamSpecInvalidSubjects),
            ("subjects", ["op..fleet"], SEStreamSpecInvalidSubjects),
            ("subjects", ["op.fleet."], SEStreamSpecInvalidSubjects),
            ("subjects", [3], SEStreamSpecInvalidSubjects),
            ("replicas", 0, SEStreamSpecInvalidReplicas),
            ("replicas", 6, SEStreamSpecInvalidReplicas),
            ("replicas", -1, SEStreamSpecInvalidReplicas),
            ("replicas", True, SEStreamSpecInvalidReplicas),
            ("replicas", 1.5, SEStreamSpecInvalidReplicas),
            ("replicas", "3", SEStreamSpecInvalidReplicas),
            ("storage", "disk", SEStreamSpecInvalidStorage),
            ("storage", 3, SEStreamSpecInvalidStorage),
            ("retention", "forever", SEStreamSpecInvalidRetention),
            ("retention", 3, SEStreamSpecInvalidRetention),
            ("duplicate_window_s", 0, SEStreamSpecInvalidDuplicateWindow),
            ("duplicate_window_s", -1.0, SEStreamSpecInvalidDuplicateWindow),
            ("duplicate_window_s", True, SEStreamSpecInvalidDuplicateWindow),
            ("duplicate_window_s", "120", SEStreamSpecInvalidDuplicateWindow),
            ("sources", "EDGE", SEStreamSpecInvalidSources),
            ("sources", 3, SEStreamSpecInvalidSources),
            ("sources", [3], SEStreamSpecInvalidSources),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    def test_the_bounds_of_replicas(self) -> None:
        assert StreamSpec.REPLICAS_MIN == 1
        assert StreamSpec.REPLICAS_MAX == 5

    @pytest.mark.parametrize("replicas", [1, 5])
    def test_the_bounds_of_replicas_are_accepted(self, replicas: int) -> None:
        assert self.build(replicas=replicas).replicas == replicas

    def test_the_storage_is_accepted_as_a_member_or_as_its_value(self) -> None:
        assert self.build(storage=StreamStorage.MEMORY.value).storage == StreamStorage.MEMORY
        assert StreamSpec(name="EVENTS", subjects=["a"], storage=StreamStorage.MEMORY).storage == StreamStorage.MEMORY

    def test_the_retention_is_accepted_as_a_member_or_as_its_value(self) -> None:
        assert self.build(retention=StreamRetention.INTEREST.value).retention == StreamRetention.INTEREST
        spec = StreamSpec(name="EVENTS", subjects=["a"], retention=StreamRetention.INTEREST)
        assert spec.retention == StreamRetention.INTEREST

    def test_a_source_given_as_a_mapping_becomes_a_stream_source(self) -> None:
        spec = self.build()
        assert isinstance(spec.sources[0], StreamSource)
        assert spec.sources[0].name == "EDGE_EVENTS"

    def test_a_mapping_source_with_a_bad_name_raises_the_source_error_unchanged(self) -> None:
        with pytest.raises(SEStreamSourceInvalidName):
            self.build(sources=self.BAD_SOURCES)

    def test_a_spec_with_only_sources_is_accepted(self) -> None:
        assert self.build(subjects=[]).subjects == []

    def test_a_spec_with_only_subjects_is_accepted(self) -> None:
        assert self.build(sources=[]).sources == []

    def test_a_spec_with_neither_subjects_nor_sources_is_refused(self) -> None:
        with pytest.raises(SEStreamSpecNoSubjectsNorSources):
            self.build(subjects=[], sources=[])

    def test_a_spec_given_nothing_but_a_name_is_refused(self) -> None:
        with pytest.raises(SEStreamSpecNoSubjectsNorSources):
            StreamSpec(name="EVENTS")

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_spec_is_refused(self) -> None:
        spec = self.build()
        with pytest.raises(ValidationError):
            spec.replicas = 1

    def test_round_trip(self) -> None:
        spec = self.build()
        assert StreamSpec.model_validate(spec.model_dump()) == spec
        assert StreamSpec.model_validate_json(spec.model_dump_json()) == spec

    def test_the_exception_hierarchy(self) -> None:
        assert not issubclass(SEInvalidStreamSpecException, ValueError)
        for error in (
            SEStreamSpecInvalidName,
            SEStreamSpecInvalidSubjects,
            SEStreamSpecInvalidReplicas,
            SEStreamSpecInvalidStorage,
            SEStreamSpecInvalidRetention,
            SEStreamSpecInvalidDuplicateWindow,
            SEStreamSpecInvalidSources,
            SEStreamSpecNoSubjectsNorSources,
        ):
            assert issubclass(error, SEInvalidStreamSpecException)
