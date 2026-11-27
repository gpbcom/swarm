from __future__ import annotations

# Standard library imports
from typing import Dict, List, Union

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.operators.exceptions import (
    SEInvalidOperatorEntryException,
    SEOperatorEntryInvalidAnchoring,
    SEOperatorEntryInvalidDeployment,
    SEOperatorEntryInvalidFirstMissionPlannerEmail,
    SEOperatorEntryInvalidFirstMissionPlannerName,
    SEOperatorEntryInvalidJurisdictions,
    SEOperatorEntryInvalidLlmProvider,
    SEOperatorEntryInvalidName,
)
from swarm_models.operators.operator_entry import OperatorEntry


class TestOperatorEntry:
    def valid(self) -> Dict[str, JsonValue]:
        return {
            "name": "  Aerowing Services  ",
            "deployment": Deployment.CLOUD.value,
            "jurisdictions": [Jurisdiction.EU_EASA.value, Jurisdiction.US_FAA.value],
            "llm_provider": LlmProvider.OPEN_WEIGHT.value,
            "anchoring": Anchoring.PUBLIC_BLOCKCHAIN.value,
            "first_mission_planner_name": "  Ada Lovelace ",
            "first_mission_planner_email": " ada@aerowing.example ",
        }

    def test_defaults(self) -> None:
        entry = OperatorEntry.model_validate({})
        assert entry.name is None
        assert entry.deployment is None
        assert entry.jurisdictions == []
        assert entry.llm_provider is None
        assert entry.anchoring == Anchoring.QUALIFIED_TIMESTAMPING
        assert entry.first_mission_planner_name is None
        assert entry.first_mission_planner_email is None

    def test_full_valid_construction(self) -> None:
        entry = OperatorEntry.model_validate(self.valid())
        assert entry.name == "Aerowing Services"
        assert entry.deployment == Deployment.CLOUD
        assert entry.jurisdictions == [Jurisdiction.EU_EASA, Jurisdiction.US_FAA]
        assert entry.llm_provider == LlmProvider.OPEN_WEIGHT
        assert entry.anchoring == Anchoring.PUBLIC_BLOCKCHAIN
        assert entry.first_mission_planner_name == "Ada Lovelace"
        assert entry.first_mission_planner_email == "ada@aerowing.example"

    @pytest.mark.parametrize("name", ["name", "deployment", "llm_provider", "first_mission_planner_email"])
    def test_none_becomes_the_default(self, name: str) -> None:
        data = self.valid()
        data[name] = None
        assert getattr(OperatorEntry.model_validate(data), name) is None

    @pytest.mark.parametrize(
        ("name", "default"),
        [("anchoring", Anchoring.QUALIFIED_TIMESTAMPING), ("jurisdictions", [])],
    )
    def test_none_becomes_the_default_of_a_field_with_a_value(
        self, name: str, default: Union[Anchoring, List[Jurisdiction]]
    ) -> None:
        data = self.valid()
        data[name] = None
        assert getattr(OperatorEntry.model_validate(data), name) == default

    @pytest.mark.parametrize("name", ["name", "first_mission_planner_name", "first_mission_planner_email"])
    @pytest.mark.parametrize("blank", ["", "   "])
    def test_a_blank_text_becomes_none(self, name: str, blank: str) -> None:
        data = self.valid()
        data[name] = blank
        assert getattr(OperatorEntry.model_validate(data), name) is None

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("name", 3, SEOperatorEntryInvalidName),
            ("deployment", "moon", SEOperatorEntryInvalidDeployment),
            ("deployment", 1, SEOperatorEntryInvalidDeployment),
            ("jurisdictions", ["eu_easa", "eu_easa"], SEOperatorEntryInvalidJurisdictions),
            ("jurisdictions", ["mars"], SEOperatorEntryInvalidJurisdictions),
            ("jurisdictions", "eu_easa", SEOperatorEntryInvalidJurisdictions),
            ("llm_provider", "gpt", SEOperatorEntryInvalidLlmProvider),
            ("anchoring", "stamp", SEOperatorEntryInvalidAnchoring),
            ("first_mission_planner_name", 3, SEOperatorEntryInvalidFirstMissionPlannerName),
            ("first_mission_planner_email", 3, SEOperatorEntryInvalidFirstMissionPlannerEmail),
            ("first_mission_planner_email", "ada.aerowing.example", SEOperatorEntryInvalidFirstMissionPlannerEmail),
            ("first_mission_planner_email", "a@b@c.example", SEOperatorEntryInvalidFirstMissionPlannerEmail),
            ("first_mission_planner_email", "ada@aerowing", SEOperatorEntryInvalidFirstMissionPlannerEmail),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(ValidationError) as caught:
            OperatorEntry.model_validate(data)
        assert isinstance(caught.value.errors()[0]["ctx"]["error"], error)

    def test_every_exception_is_a_value_error_of_the_model_base(self) -> None:
        assert issubclass(SEInvalidOperatorEntryException, ValueError)
        assert issubclass(SEOperatorEntryInvalidDeployment, SEInvalidOperatorEntryException)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            OperatorEntry.model_validate(data)

    def test_round_trip(self) -> None:
        entry = OperatorEntry.model_validate(self.valid())
        assert OperatorEntry.model_validate(entry.model_dump()) == entry
        assert OperatorEntry.model_validate_json(entry.model_dump_json()) == entry
