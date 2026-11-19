from __future__ import annotations

from typing import Dict
from uuid import UUID

import pytest
from pydantic import JsonValue, ValidationError

from swarm_models.models.operators.exceptions import (
    SEInvalidOperatorException,
    SEOperatorInvalidId,
    SEOperatorInvalidName,
)
from swarm_models.models.operators.operator import Operator


class TestOperator:
    VALID_ID: str = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    V4_ID: str = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"

    def valid(self) -> Dict[str, JsonValue]:
        return {"id": self.VALID_ID, "name": "  Ada Lovelace  "}

    def test_defaults(self) -> None:
        for name in ("id", "name"):
            assert Operator.model_fields[name].is_required()

    def test_full_valid_construction(self) -> None:
        operator = Operator.model_validate(self.valid())
        assert operator.id == UUID(self.VALID_ID)
        assert operator.name == "Ada Lovelace"

    @pytest.mark.parametrize(
        ("name", "error"),
        [("id", SEOperatorInvalidId), ("name", SEOperatorInvalidName)],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception]) -> None:
        """No field has a default, so None is refused with the exception of that field."""
        data = self.valid()
        data[name] = None
        with pytest.raises(error):
            Operator.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("id", V4_ID, SEOperatorInvalidId),
            ("id", "not-a-uuid", SEOperatorInvalidId),
            ("id", 7, SEOperatorInvalidId),
            ("id", True, SEOperatorInvalidId),
            ("name", "", SEOperatorInvalidName),
            ("name", "   ", SEOperatorInvalidName),
            ("name", 3, SEOperatorInvalidName),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(error):
            Operator.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            Operator.model_validate(data)

    def test_round_trip(self) -> None:
        operator = Operator.model_validate(self.valid())
        assert Operator.model_validate(operator.model_dump()) == operator
        assert Operator.model_validate_json(operator.model_dump_json()) == operator

    @pytest.mark.parametrize("error", [SEOperatorInvalidId, SEOperatorInvalidName])
    def test_every_field_exception_belongs_to_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidOperatorException)
        assert not issubclass(error, ValueError)
        assert not issubclass(SEInvalidOperatorException, ValueError)
