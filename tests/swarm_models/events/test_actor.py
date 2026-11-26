from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.models.events.actor import Actor
from swarm_models.models.events.enums import ActorKind
from swarm_models.models.events.exceptions import (
    SEActorInconsistentKind,
    SEActorInvalidAgentName,
    SEActorInvalidKind,
    SEActorInvalidPersonId,
    SEInvalidActorException,
)


class TestActor:
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f")
    PERSON: ClassVar[Dict[str, JsonValue]] = {"kind": "person", "person_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"}
    SWARM_AGENT: ClassVar[Dict[str, JsonValue]] = {"kind": "swarm_agent", "agent_name": "planner"}
    OUTSIDE: ClassVar[Dict[str, JsonValue]] = {
        "kind": "outside_agent",
        "person_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f",
        "agent_name": "planner",
    }

    def test_defaults(self) -> None:
        actor = Actor(kind=ActorKind.SWARM_AGENT, agent_name="planner")
        assert actor.person_id is None
        assert actor.agent_name == "planner"

    def test_full_valid_construction(self) -> None:
        actor = Actor(kind="outside_agent", person_id=self.PERSON_ID, agent_name="  planner  ")
        assert actor.kind is ActorKind.OUTSIDE_AGENT
        assert actor.person_id == self.PERSON_ID
        assert actor.agent_name == "planner"

    @pytest.mark.parametrize(("name", "base"), [("person_id", SWARM_AGENT), ("agent_name", PERSON)])
    def test_none_becomes_the_default(self, name: str, base: Dict[str, JsonValue]) -> None:
        values: Dict[str, JsonValue] = {**base, name: None}
        actor = Actor.model_validate(values)
        assert getattr(actor, name) == Actor.model_fields[name].get_default()

    def test_none_for_the_kind_is_refused(self) -> None:
        with pytest.raises(SEActorInvalidKind):
            Actor.model_validate({"kind": None, "person_id": str(self.PERSON_ID)})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("kind", "robot", SEActorInvalidKind),
            ("kind", "", SEActorInvalidKind),
            ("kind", 3, SEActorInvalidKind),
            ("kind", True, SEActorInvalidKind),
            ("kind", 1.5, SEActorInvalidKind),
            ("person_id", "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f", SEActorInvalidPersonId),
            ("person_id", "not-a-uuid", SEActorInvalidPersonId),
            ("person_id", 3, SEActorInvalidPersonId),
            ("person_id", True, SEActorInvalidPersonId),
            ("agent_name", "", SEActorInvalidAgentName),
            ("agent_name", "   ", SEActorInvalidAgentName),
            ("agent_name", 3, SEActorInvalidAgentName),
            ("agent_name", True, SEActorInvalidAgentName),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        values: Dict[str, JsonValue] = dict(self.OUTSIDE)
        values[name] = value
        with pytest.raises(error):
            Actor.model_validate(values)

    @pytest.mark.parametrize(
        "values",
        [
            {"kind": "person"},
            {"kind": "person", "person_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f", "agent_name": "planner"},
            {"kind": "person", "agent_name": "planner"},
            {"kind": "swarm_agent"},
            {"kind": "swarm_agent", "person_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"},
            {"kind": "outside_agent"},
            {"kind": "outside_agent", "agent_name": "planner"},
            {"kind": "outside_agent", "person_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"},
        ],
    )
    def test_an_inconsistent_kind_is_refused(self, values: Dict[str, JsonValue]) -> None:
        with pytest.raises(SEActorInconsistentKind):
            Actor.model_validate(values)

    def test_a_person_needs_only_a_person_id(self) -> None:
        actor = Actor.model_validate(self.PERSON)
        assert actor.kind is ActorKind.PERSON
        assert actor.agent_name is None

    def test_a_swarm_agent_may_act_for_a_person(self) -> None:
        actor = Actor(kind=ActorKind.SWARM_AGENT, agent_name="planner", person_id=self.PERSON_ID)
        assert actor.person_id == self.PERSON_ID

    def test_an_outside_agent_is_accepted_with_its_person(self) -> None:
        actor = Actor.model_validate(self.OUTSIDE)
        assert actor.kind is ActorKind.OUTSIDE_AGENT
        assert actor.person_id == self.PERSON_ID
        assert actor.agent_name == "planner"

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            Actor.model_validate({**self.PERSON, "extra": 1})

    def test_assigning_a_field_of_a_built_actor_is_refused(self) -> None:
        actor = Actor.model_validate(self.PERSON)
        with pytest.raises(ValidationError):
            actor.agent_name = "planner"

    @pytest.mark.parametrize("values", [PERSON, OUTSIDE])
    def test_round_trip(self, values: Dict[str, JsonValue]) -> None:
        actor = Actor.model_validate(values)
        assert Actor.model_validate(actor.model_dump()) == actor
        assert Actor.model_validate_json(actor.model_dump_json()) == actor

    def test_the_exception_hierarchy(self) -> None:
        assert issubclass(SEInvalidActorException, Exception)
        assert not issubclass(SEInvalidActorException, ValueError)
        for error in (
            SEActorInvalidKind,
            SEActorInvalidPersonId,
            SEActorInvalidAgentName,
            SEActorInconsistentKind,
        ):
            assert issubclass(error, SEInvalidActorException)
