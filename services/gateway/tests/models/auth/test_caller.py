from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Optional
from uuid import UUID, uuid1, uuid4

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from gateway.models.auth.caller import Caller
from gateway.models.auth.exceptions import (
    SECallerInvalidOperatorId,
    SECallerInvalidPersonId,
    SECallerInvalidRoles,
    SECallerOperatorMismatch,
    SEInvalidCallerException,
)
from swarm_models.models.people.enums import RoleName


class TestCaller:
    PERSON: ClassVar[UUID] = uuid4()
    OPERATOR: ClassVar[UUID] = uuid4()
    OPERATOR_ROLES: ClassVar[List[RoleName]] = [role for role in RoleName if role is not RoleName.SWARM_ADMINISTRATOR]
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SECallerInvalidPersonId,
        SECallerInvalidOperatorId,
        SECallerInvalidRoles,
        SECallerOperatorMismatch,
    ]
    FULL: ClassVar[Dict[str, JsonValue]] = {
        "person_id": str(PERSON),
        "operator_id": str(OPERATOR),
        "roles": [RoleName.PILOT.value, RoleName.INSTRUCTOR.value],
    }
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"person_id": str(PERSON), "colour": "red"}
    BAD_PERSON_ID_CONFIGURATIONS: ClassVar[List[JsonValue]] = [None, "", "not-a-uuid", 3, True]

    def test_defaults(self) -> None:
        caller = Caller.model_validate({"person_id": str(self.PERSON)})
        assert caller.person_id == self.PERSON
        assert caller.operator_id is None
        assert caller.roles == []

    def test_full_valid_construction(self) -> None:
        caller = Caller.model_validate(self.FULL)
        assert caller.person_id == self.PERSON
        assert caller.operator_id == self.OPERATOR
        assert caller.roles == [RoleName.PILOT, RoleName.INSTRUCTOR]

    @pytest.mark.parametrize("name", ["operator_id", "roles"])
    def test_none_becomes_the_default(self, name: str) -> None:
        caller = Caller.model_validate({"person_id": str(self.PERSON), name: None})
        default = Caller.model_fields[name].get_default(call_default_factory=True)
        assert getattr(caller, name) == default

    def test_the_person_id_has_no_default(self) -> None:
        assert Caller.model_fields["person_id"].is_required()

    @pytest.mark.parametrize("value", BAD_PERSON_ID_CONFIGURATIONS)
    def test_a_bad_person_id_is_refused(self, value: JsonValue) -> None:
        with pytest.raises(SECallerInvalidPersonId):
            Caller.model_validate({"person_id": value})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("operator_id", "", SECallerInvalidOperatorId),
            ("operator_id", "not-a-uuid", SECallerInvalidOperatorId),
            ("operator_id", 3, SECallerInvalidOperatorId),
            ("operator_id", True, SECallerInvalidOperatorId),
            ("roles", "pilot", SECallerInvalidRoles),
            ("roles", 3, SECallerInvalidRoles),
            ("roles", ["unknown_role"], SECallerInvalidRoles),
            ("roles", [3], SECallerInvalidRoles),
            ("roles", [RoleName.PILOT.value, RoleName.PILOT.value], SECallerInvalidRoles),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            Caller.model_validate({"person_id": str(self.PERSON), name: value})

    def test_a_missing_person_id_is_refused(self) -> None:
        with pytest.raises((ValidationError, SECallerInvalidPersonId)):
            Caller.model_validate({})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            Caller.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        caller = Caller.model_validate(self.FULL)
        assert Caller.model_validate(caller.model_dump()) == caller

    def test_the_model_is_frozen(self) -> None:
        caller = Caller.model_validate(self.FULL)
        with pytest.raises(ValidationError):
            caller.operator_id = None

    @pytest.mark.parametrize("person_id", [uuid1(), uuid4()])
    def test_a_person_id_of_any_version_is_accepted(self, person_id: UUID) -> None:
        assert Caller.model_validate({"person_id": str(person_id)}).person_id == person_id

    @pytest.mark.parametrize("role", OPERATOR_ROLES)
    def test_an_operator_role_with_an_operator_is_accepted(self, role: RoleName) -> None:
        caller = Caller.model_validate(
            {"person_id": str(self.PERSON), "operator_id": str(self.OPERATOR), "roles": [role.value]}
        )
        assert caller.roles == [role]

    @pytest.mark.parametrize("role", OPERATOR_ROLES)
    def test_an_operator_role_without_an_operator_is_refused(self, role: RoleName) -> None:
        with pytest.raises(SECallerOperatorMismatch):
            Caller.model_validate({"person_id": str(self.PERSON), "roles": [role.value]})

    def test_the_swarm_administrator_without_an_operator_is_accepted(self) -> None:
        caller = Caller.model_validate({"person_id": str(self.PERSON), "roles": [RoleName.SWARM_ADMINISTRATOR.value]})
        assert caller.operator_id is None
        assert caller.roles == [RoleName.SWARM_ADMINISTRATOR]

    def test_the_swarm_administrator_with_an_operator_is_refused(self) -> None:
        with pytest.raises(SECallerOperatorMismatch):
            Caller.model_validate(
                {
                    "person_id": str(self.PERSON),
                    "operator_id": str(self.OPERATOR),
                    "roles": [RoleName.SWARM_ADMINISTRATOR.value],
                }
            )

    @pytest.mark.parametrize("operator_id", [None, str(OPERATOR)])
    def test_the_administrator_together_with_an_operator_role_is_refused(self, operator_id: Optional[str]) -> None:
        with pytest.raises(SECallerOperatorMismatch):
            Caller.model_validate(
                {
                    "person_id": str(self.PERSON),
                    "operator_id": operator_id,
                    "roles": [RoleName.SWARM_ADMINISTRATOR.value, RoleName.PILOT.value],
                }
            )

    @pytest.mark.parametrize("operator_id", [None, str(OPERATOR)])
    def test_no_roles_accepts_any_operator_id(self, operator_id: Optional[str]) -> None:
        caller = Caller.model_validate({"person_id": str(self.PERSON), "operator_id": operator_id, "roles": []})
        assert caller.roles == []

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidCallerException)
