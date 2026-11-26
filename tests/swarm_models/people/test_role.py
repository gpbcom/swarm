from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Optional, Type
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from swarm_models.people.enums import RoleName
from swarm_models.people.exceptions import (
    SEInvalidRoleException,
    SERoleInvalidName,
    SERoleInvalidOperatorId,
    SERoleInvalidPersonId,
    SERoleOperatorMismatch,
)
from swarm_models.people.role import Role


class TestRole:
    PERSON_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    OPERATOR_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    V4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    OPERATOR_ROLES: ClassVar[List[str]] = [
        "pilot",
        "mission_planner",
        "fleet_maintainer",
        "instructor",
        "client",
        "site_agent",
    ]

    def valid(self) -> Dict[str, JsonValue]:
        return {"person_id": self.PERSON_ID, "operator_id": self.OPERATOR_ID, "name": "pilot"}

    def test_defaults(self) -> None:
        role = Role.model_validate({"person_id": self.PERSON_ID, "name": "swarm_administrator"})
        assert role.operator_id is None
        assert role.name is RoleName.SWARM_ADMINISTRATOR

    def test_full_valid_construction(self) -> None:
        role = Role.model_validate(self.valid())
        assert role.person_id == UUID(self.PERSON_ID)
        assert role.operator_id == UUID(self.OPERATOR_ID)
        assert role.name is RoleName.PILOT

    def test_a_member_is_accepted_as_a_name(self) -> None:
        role = Role.model_validate({**self.valid(), "name": RoleName.INSTRUCTOR})
        assert role.name is RoleName.INSTRUCTOR

    @pytest.mark.parametrize("name", OPERATOR_ROLES)
    def test_every_other_role_needs_an_operator(self, name: str) -> None:
        assert Role.model_validate({**self.valid(), "name": name}).name == name
        with pytest.raises(SERoleOperatorMismatch):
            Role.model_validate({"person_id": self.PERSON_ID, "name": name})

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("operator_id", None),
            ("person_id", SERoleInvalidPersonId),
            ("name", SERoleInvalidName),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: Optional[Type[Exception]]) -> None:
        data = {"person_id": self.PERSON_ID, "name": "swarm_administrator", name: None}
        if error is None:
            assert Role.model_validate(data).operator_id is None
        else:
            with pytest.raises(error):
                Role.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("person_id", V4, SERoleInvalidPersonId),
            ("person_id", True, SERoleInvalidPersonId),
            ("person_id", "  ", SERoleInvalidPersonId),
            ("person_id", 5, SERoleInvalidPersonId),
            ("operator_id", V4, SERoleInvalidOperatorId),
            ("operator_id", True, SERoleInvalidOperatorId),
            ("operator_id", "  ", SERoleInvalidOperatorId),
            ("operator_id", 5, SERoleInvalidOperatorId),
            ("name", "pilot-in-chief", SERoleInvalidName),
            ("name", "  ", SERoleInvalidName),
            ("name", True, SERoleInvalidName),
            ("name", 5, SERoleInvalidName),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: Type[Exception]) -> None:
        with pytest.raises(error):
            Role.model_validate({**self.valid(), name: value})

    def test_a_swarm_administrator_with_an_operator_is_refused(self) -> None:
        with pytest.raises(SERoleOperatorMismatch):
            Role.model_validate({**self.valid(), "name": "swarm_administrator"})

    def test_a_pilot_without_an_operator_is_refused(self) -> None:
        with pytest.raises(SERoleOperatorMismatch):
            Role.model_validate({"person_id": self.PERSON_ID, "name": "pilot"})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValueError):
            Role.model_validate({**self.valid(), "scope": "all"})

    def test_it_is_not_frozen(self) -> None:
        role = Role.model_validate(self.valid())
        role.name = RoleName.CLIENT
        assert role.name is RoleName.CLIENT

    def test_round_trip(self) -> None:
        role = Role.model_validate(self.valid())
        assert Role.model_validate(role.model_dump()) == role
        assert Role.model_validate_json(role.model_dump_json()) == role

    def test_the_exceptions_share_their_base(self) -> None:
        errors: List[Type[Exception]] = [
            SERoleInvalidPersonId,
            SERoleInvalidOperatorId,
            SERoleInvalidName,
            SERoleOperatorMismatch,
        ]
        assert issubclass(SEInvalidRoleException, Exception)
        assert not issubclass(SEInvalidRoleException, ValueError)
        assert all(issubclass(error, SEInvalidRoleException) for error in errors)
