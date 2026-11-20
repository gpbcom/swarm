from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Optional, Type
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from swarm_models.models.people.exceptions import (
    SEInvalidPersonException,
    SEPersonInvalidEmail,
    SEPersonInvalidId,
    SEPersonInvalidName,
    SEPersonInvalidOperatorId,
)
from swarm_models.models.people.person import Person


class TestPerson:
    ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    OPERATOR_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    V4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"

    def valid(self) -> Dict[str, JsonValue]:
        return {"id": self.ID, "operator_id": self.OPERATOR_ID, "name": "Ada Lovelace", "email": "ada@example.org"}

    def test_defaults(self) -> None:
        person = Person.model_validate({"id": self.ID, "name": "Ada", "email": "ada@example.org"})
        assert person.operator_id is None

    def test_full_valid_construction(self) -> None:
        person = Person.model_validate({**self.valid(), "name": "  Ada Lovelace  ", "email": " ada@example.org "})
        assert person.id == UUID(self.ID)
        assert person.operator_id == UUID(self.OPERATOR_ID)
        assert person.name == "Ada Lovelace"
        assert person.email == "ada@example.org"

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("operator_id", None),
            ("id", SEPersonInvalidId),
            ("name", SEPersonInvalidName),
            ("email", SEPersonInvalidEmail),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: Optional[Type[Exception]]) -> None:
        data = {**self.valid(), name: None}
        if error is None:
            assert Person.model_validate(data).operator_id is None
        else:
            with pytest.raises(error):
                Person.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("id", V4, SEPersonInvalidId),
            ("id", True, SEPersonInvalidId),
            ("id", "  ", SEPersonInvalidId),
            ("id", 5, SEPersonInvalidId),
            ("operator_id", V4, SEPersonInvalidOperatorId),
            ("operator_id", True, SEPersonInvalidOperatorId),
            ("operator_id", "  ", SEPersonInvalidOperatorId),
            ("operator_id", 5, SEPersonInvalidOperatorId),
            ("name", "  ", SEPersonInvalidName),
            ("name", "", SEPersonInvalidName),
            ("name", True, SEPersonInvalidName),
            ("name", 5, SEPersonInvalidName),
            ("email", "", SEPersonInvalidEmail),
            ("email", "  ", SEPersonInvalidEmail),
            ("email", "no-at-sign", SEPersonInvalidEmail),
            ("email", "a@b@c", SEPersonInvalidEmail),
            ("email", "@example.org", SEPersonInvalidEmail),
            ("email", "ada@", SEPersonInvalidEmail),
            ("email", "ada lovelace@example.org", SEPersonInvalidEmail),
            ("email", True, SEPersonInvalidEmail),
            ("email", 5, SEPersonInvalidEmail),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: Type[Exception]) -> None:
        with pytest.raises(error):
            Person.model_validate({**self.valid(), name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValueError):
            Person.model_validate({**self.valid(), "nickname": "Countess"})

    def test_it_is_not_frozen(self) -> None:
        person = Person.model_validate(self.valid())
        person.name = "Grace"
        assert person.name == "Grace"

    def test_round_trip(self) -> None:
        person = Person.model_validate(self.valid())
        assert Person.model_validate(person.model_dump()) == person
        assert Person.model_validate_json(person.model_dump_json()) == person

    def test_the_exceptions_share_their_base(self) -> None:
        errors: List[Type[Exception]] = [
            SEPersonInvalidId,
            SEPersonInvalidOperatorId,
            SEPersonInvalidName,
            SEPersonInvalidEmail,
        ]
        assert issubclass(SEInvalidPersonException, Exception)
        assert not issubclass(SEInvalidPersonException, ValueError)
        assert all(issubclass(error, SEInvalidPersonException) for error in errors)
