from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import ClassVar, Dict
from uuid import UUID

import pytest
from pydantic import JsonValue, ValidationError

from swarm_models.models.events.actor import Actor
from swarm_models.models.events.enums import ActorKind
from swarm_models.models.events.event import Event
from swarm_models.models.events.exceptions import (
    SEActorInvalidKind,
    SEEventInvalidActor,
    SEEventInvalidId,
    SEEventInvalidMissionId,
    SEEventInvalidOccurredAt,
    SEEventInvalidOperatorId,
    SEEventInvalidPayload,
    SEEventInvalidType,
    SEEventInvalidVersion,
    SEInvalidEventException,
)


class TestEvent:
    EVENT_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f")
    OPERATOR_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, 123456, tzinfo=UTC)
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f",
        "type": "mission.planned",
        "operator_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60",
        "occurred_at": "2026-11-19T10:30:15.123456+00:00",
        "actor": {"kind": "person", "person_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62"},
        "payload": {"name": "Survey", "legs": [1, 2]},
    }

    def build(self, **changes: object) -> Event:
        values: Dict[str, object] = dict(self.VALID)
        values.update(changes)
        return Event.model_validate(values)

    def test_defaults(self) -> None:
        event = self.build()
        assert event.version == 1
        assert event.mission_id is None
        assert event.actor == Actor(kind=ActorKind.PERSON, person_id=self.PERSON_ID)

    def test_full_valid_construction(self) -> None:
        event = Event(
            id=self.EVENT_ID,
            type="mission.planned",
            version=2,
            operator_id=self.OPERATOR_ID,
            mission_id=self.MISSION_ID,
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.SWARM_AGENT, agent_name="planner"),
            payload={"name": "Survey"},
        )
        assert event.id == self.EVENT_ID
        assert event.type == "mission.planned"
        assert event.version == 2
        assert event.operator_id == self.OPERATOR_ID
        assert event.mission_id == self.MISSION_ID
        assert event.occurred_at == self.OCCURRED_AT
        assert event.actor.agent_name == "planner"
        assert event.payload == {"name": "Survey"}

    @pytest.mark.parametrize(
        ("name", "default"),
        [("version", 1), ("mission_id", None)],
    )
    def test_none_becomes_the_default(self, name: str, default: JsonValue) -> None:
        assert getattr(self.build(**{name: None}), name) == default

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("id", SEEventInvalidId),
            ("type", SEEventInvalidType),
            ("operator_id", SEEventInvalidOperatorId),
            ("occurred_at", SEEventInvalidOccurredAt),
            ("actor", SEEventInvalidActor),
            ("payload", SEEventInvalidPayload),
        ],
    )
    def test_none_for_a_required_field_is_refused(self, name: str, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("id", "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f", SEEventInvalidId),
            ("id", "not-a-uuid", SEEventInvalidId),
            ("id", 3, SEEventInvalidId),
            ("type", "Mission.Planned", SEEventInvalidType),
            ("type", "mission", SEEventInvalidType),
            ("type", "mission..planned", SEEventInvalidType),
            ("type", "", SEEventInvalidType),
            ("type", 3, SEEventInvalidType),
            ("version", 0, SEEventInvalidVersion),
            ("version", -1, SEEventInvalidVersion),
            ("version", True, SEEventInvalidVersion),
            ("version", 1.5, SEEventInvalidVersion),
            ("version", "1", SEEventInvalidVersion),
            ("operator_id", "not-a-uuid", SEEventInvalidOperatorId),
            ("operator_id", 3, SEEventInvalidOperatorId),
            ("mission_id", "not-a-uuid", SEEventInvalidMissionId),
            ("mission_id", 3, SEEventInvalidMissionId),
            ("occurred_at", "2026-11-19T10:30:15.123456", SEEventInvalidOccurredAt),
            ("occurred_at", datetime(2026, 11, 19, 10, 30, 15), SEEventInvalidOccurredAt),
            ("occurred_at", "yesterday", SEEventInvalidOccurredAt),
            ("occurred_at", 3, SEEventInvalidOccurredAt),
            ("actor", "person", SEEventInvalidActor),
            ("actor", 3, SEEventInvalidActor),
            ("actor", [1, 2], SEEventInvalidActor),
            ("payload", [1, 2], SEEventInvalidPayload),
            ("payload", "x", SEEventInvalidPayload),
            ("payload", 3, SEEventInvalidPayload),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: object, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    def test_a_mapping_actor_with_a_bad_kind_raises_the_actor_error_unchanged(self) -> None:
        with pytest.raises(SEActorInvalidKind):
            self.build(actor={"kind": "robot", "person_id": str(self.PERSON_ID)})

    def test_an_actor_given_as_a_mapping_becomes_an_actor(self) -> None:
        assert isinstance(self.build().actor, Actor)

    def test_a_fleet_event_has_no_mission(self) -> None:
        assert self.build(mission_id=None).mission_id is None

    def test_an_offset_occurred_at_becomes_utc(self) -> None:
        event = self.build(occurred_at="2026-11-19T12:30:15.123456+02:00")
        assert event.occurred_at.utcoffset() == timedelta(0)
        assert event.occurred_at == self.OCCURRED_AT
        assert event.occurred_at.microsecond == 123456

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_event_is_refused(self) -> None:
        event = self.build()
        with pytest.raises(ValidationError):
            event.version = 2

    def test_round_trip(self) -> None:
        event = self.build(mission_id=str(self.MISSION_ID), version=3)
        assert Event.model_validate(event.model_dump()) == event
        json_form = event.model_dump_json()
        assert "10:30:15.123456" in json_form
        assert Event.model_validate_json(json_form) == event

    def test_the_exception_hierarchy(self) -> None:
        assert issubclass(SEInvalidEventException, Exception)
        assert not issubclass(SEInvalidEventException, ValueError)
        for error in (
            SEEventInvalidId,
            SEEventInvalidType,
            SEEventInvalidVersion,
            SEEventInvalidOperatorId,
            SEEventInvalidMissionId,
            SEEventInvalidOccurredAt,
            SEEventInvalidActor,
            SEEventInvalidPayload,
        ):
            assert issubclass(error, SEInvalidEventException)
