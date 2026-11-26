from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime
from typing import ClassVar, Optional
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.base.swarm_model import SwarmModel
from swarm_models.events.actor import Actor
from swarm_models.events.enums import ActorKind
from swarm_models.events.event import Event
from swarm_nats.models.subjects.exceptions import (
    SEInvalidOperatorSubjectsException,
    SEOperatorSubjectsInvalidEvent,
    SEOperatorSubjectsInvalidMissionId,
    SEOperatorSubjectsInvalidOperatorId,
    SEOperatorSubjectsOperatorMismatch,
)
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects


class TestOperatorSubjects:
    OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7b")
    OTHER_OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7c")
    MISSION_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7d")
    EVENT_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7e")
    PERSON_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7f")
    OCCURRED_AT: ClassVar[datetime] = datetime(2026, 11, 19, 10, 30, 15, 123456, tzinfo=UTC)
    EVENT_TYPE: ClassVar[str] = "mission.planned"

    def subjects(self) -> OperatorSubjects:
        return OperatorSubjects(operator_id=self.OPERATOR_ID)

    def an_event(self, operator_id: UUID, mission_id: Optional[UUID]) -> Event:
        return Event(
            id=self.EVENT_ID,
            type=self.EVENT_TYPE,
            operator_id=operator_id,
            mission_id=mission_id,
            occurred_at=self.OCCURRED_AT,
            actor=Actor(kind=ActorKind.PERSON, person_id=self.PERSON_ID),
            payload={},
        )

    def test_it_is_a_swarm_model(self) -> None:
        assert issubclass(OperatorSubjects, SwarmModel)

    def test_full_valid_construction(self) -> None:
        assert self.subjects().operator_id == self.OPERATOR_ID

    def test_the_operator_id_is_accepted_as_a_string(self) -> None:
        assert OperatorSubjects.model_validate({"operator_id": str(self.OPERATOR_ID)}).operator_id == self.OPERATOR_ID

    @pytest.mark.parametrize(
        "value",
        [
            None,
            "not-a-uuid",
            3,
            True,
            "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f",
        ],
    )
    def test_rejects_bad_values(self, value: JsonValue) -> None:
        with pytest.raises(SEOperatorSubjectsInvalidOperatorId):
            OperatorSubjects.model_validate({"operator_id": value})

    def test_an_operator_id_that_is_not_version_7_is_refused(self) -> None:
        with pytest.raises(SEOperatorSubjectsInvalidOperatorId):
            OperatorSubjects(operator_id=UUID("3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"))

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            OperatorSubjects.model_validate({"operator_id": str(self.OPERATOR_ID), "extra": 1})

    def test_assigning_a_field_of_built_subjects_is_refused(self) -> None:
        subjects = self.subjects()
        with pytest.raises(ValidationError):
            subjects.operator_id = self.OTHER_OPERATOR_ID

    def test_round_trip(self) -> None:
        subjects = self.subjects()
        assert OperatorSubjects.model_validate(subjects.model_dump()) == subjects
        assert OperatorSubjects.model_validate_json(subjects.model_dump_json()) == subjects

    def test_all_covers_everything_of_the_operator(self) -> None:
        assert self.subjects().all() == f"op.{self.OPERATOR_ID}.>"

    def test_a_mission_subject(self) -> None:
        subject = self.subjects().mission(self.MISSION_ID, self.EVENT_TYPE)
        assert subject == f"op.{self.OPERATOR_ID}.mission.{self.MISSION_ID}.{self.EVENT_TYPE}"

    def test_a_fleet_subject(self) -> None:
        assert self.subjects().fleet("drone.landed") == f"op.{self.OPERATOR_ID}.fleet.drone.landed"

    def test_an_event_of_a_mission_goes_to_the_mission_subject(self) -> None:
        event = self.an_event(self.OPERATOR_ID, self.MISSION_ID)
        subject = self.subjects().for_event(event)
        assert subject == f"op.{self.OPERATOR_ID}.mission.{self.MISSION_ID}.{self.EVENT_TYPE}"

    def test_an_event_without_a_mission_goes_to_the_fleet_subject(self) -> None:
        event = self.an_event(self.OPERATOR_ID, None)
        assert self.subjects().for_event(event) == f"op.{self.OPERATOR_ID}.fleet.{self.EVENT_TYPE}"

    def test_the_subjects_of_two_operators_never_overlap(self) -> None:
        other = OperatorSubjects(operator_id=self.OTHER_OPERATOR_ID)
        assert self.subjects().fleet("drone.landed") != other.fleet("drone.landed")
        assert not self.subjects().fleet("drone.landed").startswith(other.all()[:-1])

    @pytest.mark.parametrize("event", ["", "Mission.Planned", "mission.*", ">", "a b", "mission..x"])
    def test_a_bad_event_name_is_refused(self, event: str) -> None:
        with pytest.raises(SEOperatorSubjectsInvalidEvent):
            self.subjects().fleet(event)
        with pytest.raises(SEOperatorSubjectsInvalidEvent):
            self.subjects().mission(self.MISSION_ID, event)

    @pytest.mark.parametrize("event", ["landed", "drone.landed", "a1_b.c_2"])
    def test_a_good_event_name_is_accepted(self, event: str) -> None:
        assert self.subjects().fleet(event).endswith(f".fleet.{event}")

    def test_an_event_of_another_operator_is_refused(self) -> None:
        with pytest.raises(SEOperatorSubjectsOperatorMismatch):
            self.subjects().for_event(self.an_event(self.OTHER_OPERATOR_ID, self.MISSION_ID))

    def test_a_fleet_event_of_another_operator_is_refused(self) -> None:
        with pytest.raises(SEOperatorSubjectsOperatorMismatch):
            self.subjects().for_event(self.an_event(self.OTHER_OPERATOR_ID, None))

    @pytest.mark.parametrize("mission_id", ["not-a-uuid", 3, None])
    def test_a_mission_id_that_is_not_a_uuid_is_refused(self, mission_id: JsonValue) -> None:
        with pytest.raises(SEOperatorSubjectsInvalidMissionId):
            self.subjects().mission(mission_id, self.EVENT_TYPE)

    def test_the_exception_hierarchy(self) -> None:
        assert not issubclass(SEInvalidOperatorSubjectsException, ValueError)
        for error in (
            SEOperatorSubjectsInvalidOperatorId,
            SEOperatorSubjectsInvalidMissionId,
            SEOperatorSubjectsInvalidEvent,
            SEOperatorSubjectsOperatorMismatch,
        ):
            assert issubclass(error, SEInvalidOperatorSubjectsException)
