from __future__ import annotations

# Standard library imports
from typing import Dict, Union
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.operators.exceptions import (
    SEInvalidOperatorException,
    SEOperatorInvalidAnchoring,
    SEOperatorInvalidDeployment,
    SEOperatorInvalidId,
    SEOperatorInvalidJurisdictions,
    SEOperatorInvalidLlmProvider,
    SEOperatorInvalidName,
)
from swarm_models.operators.operator import Operator


class TestOperator:
    VALID_ID: str = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    V4_ID: str = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"

    def valid(self) -> Dict[str, JsonValue]:
        return {
            "id": self.VALID_ID,
            "name": "  Aerowing Services  ",
            "deployment": Deployment.ON_PREMISES.value,
            "jurisdictions": [Jurisdiction.EU_EASA.value, Jurisdiction.US_FAA.value],
            "llm_provider": LlmProvider.OPEN_WEIGHT.value,
            "anchoring": Anchoring.NONE.value,
        }

    def minimal(self) -> Dict[str, JsonValue]:
        return {
            "id": self.VALID_ID,
            "name": "Aerowing Services",
            "deployment": Deployment.CLOUD.value,
            "jurisdictions": [Jurisdiction.EU_EASA.value],
        }

    def test_defaults(self) -> None:
        for name in ("id", "name", "deployment", "jurisdictions"):
            assert Operator.model_fields[name].is_required()
        operator = Operator.model_validate(self.minimal())
        assert operator.llm_provider == LlmProvider.CLAUDE
        assert operator.anchoring == Anchoring.QUALIFIED_TIMESTAMPING

    def test_full_valid_construction(self) -> None:
        operator = Operator.model_validate(self.valid())
        assert operator.id == UUID(self.VALID_ID)
        assert operator.name == "Aerowing Services"
        assert operator.deployment == Deployment.ON_PREMISES
        assert operator.jurisdictions == [Jurisdiction.EU_EASA, Jurisdiction.US_FAA]
        assert operator.llm_provider == LlmProvider.OPEN_WEIGHT
        assert operator.anchoring == Anchoring.NONE

    @pytest.mark.parametrize(
        ("name", "default"),
        [("llm_provider", LlmProvider.CLAUDE), ("anchoring", Anchoring.QUALIFIED_TIMESTAMPING)],
    )
    def test_none_becomes_the_default(self, name: str, default: Union[LlmProvider, Anchoring]) -> None:
        data = self.valid()
        data[name] = None
        assert getattr(Operator.model_validate(data), name) == default

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("id", SEOperatorInvalidId),
            ("name", SEOperatorInvalidName),
            ("deployment", SEOperatorInvalidDeployment),
            ("jurisdictions", SEOperatorInvalidJurisdictions),
        ],
    )
    def test_a_required_field_set_to_none_is_refused(self, name: str, error: type[Exception]) -> None:
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
            ("deployment", "moon", SEOperatorInvalidDeployment),
            ("deployment", 1, SEOperatorInvalidDeployment),
            ("jurisdictions", [], SEOperatorInvalidJurisdictions),
            ("jurisdictions", ["eu_easa", "eu_easa"], SEOperatorInvalidJurisdictions),
            ("jurisdictions", ["mars"], SEOperatorInvalidJurisdictions),
            ("jurisdictions", "eu_easa", SEOperatorInvalidJurisdictions),
            ("llm_provider", "gpt", SEOperatorInvalidLlmProvider),
            ("llm_provider", 1, SEOperatorInvalidLlmProvider),
            ("anchoring", "stamp", SEOperatorInvalidAnchoring),
            ("anchoring", 1, SEOperatorInvalidAnchoring),
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

    @pytest.mark.parametrize(
        "error",
        [
            SEOperatorInvalidId,
            SEOperatorInvalidName,
            SEOperatorInvalidDeployment,
            SEOperatorInvalidJurisdictions,
            SEOperatorInvalidLlmProvider,
            SEOperatorInvalidAnchoring,
        ],
    )
    def test_every_field_exception_belongs_to_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidOperatorException)
        assert not issubclass(error, ValueError)
        assert not issubclass(SEInvalidOperatorException, ValueError)
