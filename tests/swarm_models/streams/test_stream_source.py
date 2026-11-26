from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.streams.exceptions import (
    SEInvalidStreamSourceException,
    SEStreamSourceInvalidDomain,
    SEStreamSourceInvalidFilterSubject,
    SEStreamSourceInvalidName,
)
from swarm_models.streams.stream_source import StreamSource


class TestStreamSource:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "name": "EDGE_EVENTS",
        "domain": "edge-1",
        "filter_subject": "op.*.fleet.>",
    }

    def build(self, **changes: JsonValue) -> StreamSource:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return StreamSource.model_validate(values)

    def test_defaults(self) -> None:
        source = StreamSource(name="EDGE_EVENTS")
        assert source.name == "EDGE_EVENTS"
        assert source.domain is None
        assert source.filter_subject is None

    def test_full_valid_construction(self) -> None:
        source = StreamSource(name="EDGE_EVENTS", domain="edge-1", filter_subject="op.*.fleet.>")
        assert source.name == "EDGE_EVENTS"
        assert source.domain == "edge-1"
        assert source.filter_subject == "op.*.fleet.>"

    @pytest.mark.parametrize("name", ["domain", "filter_subject"])
    def test_none_becomes_the_default(self, name: str) -> None:
        assert getattr(self.build(**{name: None}), name) is None

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("name", None, SEStreamSourceInvalidName),
            ("name", "", SEStreamSourceInvalidName),
            ("name", "   ", SEStreamSourceInvalidName),
            ("name", "a b", SEStreamSourceInvalidName),
            ("name", "a.b", SEStreamSourceInvalidName),
            ("name", "a*", SEStreamSourceInvalidName),
            ("name", 3, SEStreamSourceInvalidName),
            ("name", True, SEStreamSourceInvalidName),
            ("domain", "", SEStreamSourceInvalidDomain),
            ("domain", "a b", SEStreamSourceInvalidDomain),
            ("domain", "a.b", SEStreamSourceInvalidDomain),
            ("domain", 3, SEStreamSourceInvalidDomain),
            ("filter_subject", "", SEStreamSourceInvalidFilterSubject),
            ("filter_subject", "op. fleet", SEStreamSourceInvalidFilterSubject),
            ("filter_subject", "op..fleet", SEStreamSourceInvalidFilterSubject),
            ("filter_subject", ".op", SEStreamSourceInvalidFilterSubject),
            ("filter_subject", "op.", SEStreamSourceInvalidFilterSubject),
            ("filter_subject", 3, SEStreamSourceInvalidFilterSubject),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    def test_the_field_exceptions_subclass_the_base_of_the_model(self) -> None:
        assert not issubclass(SEInvalidStreamSourceException, ValueError)
        for error in (SEStreamSourceInvalidName, SEStreamSourceInvalidDomain, SEStreamSourceInvalidFilterSubject):
            assert issubclass(error, SEInvalidStreamSourceException)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_source_is_refused(self) -> None:
        source = self.build()
        with pytest.raises(ValidationError):
            source.name = "OTHER"

    def test_round_trip(self) -> None:
        source = self.build()
        assert StreamSource.model_validate(source.model_dump()) == source
        assert StreamSource.model_validate_json(source.model_dump_json()) == source
