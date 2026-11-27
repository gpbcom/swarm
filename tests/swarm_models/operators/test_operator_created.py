from __future__ import annotations

# Standard library imports
from typing import Dict, Optional

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.operators.exceptions import (
    SEOperatorCreatedForeignCellAssignment,
    SEOperatorCreatedForeignPerson,
)
from swarm_models.operators.operator_created import OperatorCreated


class TestOperatorCreated:
    OPERATOR_ID: str = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    OTHER_ID: str = "01943c5e-8a4b-7d00-8000-000000000001"
    PERSON_ID: str = "01943c5e-8a4b-7d00-8000-000000000002"

    def assignment(self, operator_id: str) -> Dict[str, JsonValue]:
        return {"operator_id": operator_id, "cell": "cell-eu-1", "assigned_at": "2027-01-18T09:30:00+00:00"}

    def person(self, operator_id: Optional[str]) -> Dict[str, JsonValue]:
        return {
            "id": self.PERSON_ID,
            "operator_id": operator_id,
            "name": "Ada Lovelace",
            "email": "ada@aerowing.example",
        }

    def valid(self) -> Dict[str, JsonValue]:
        return {
            "operator": {
                "id": self.OPERATOR_ID,
                "name": "Aerowing Services",
                "deployment": "cloud",
                "jurisdictions": ["eu_easa"],
            },
            "cell_assignment": self.assignment(self.OPERATOR_ID),
            "first_mission_planner": self.person(self.OPERATOR_ID),
        }

    def test_defaults(self) -> None:
        for name in ("operator", "cell_assignment", "first_mission_planner"):
            assert OperatorCreated.model_fields[name].is_required()

    def test_full_valid_construction(self) -> None:
        created = OperatorCreated.model_validate(self.valid())
        assert created.operator.name == "Aerowing Services"
        assert created.cell_assignment.operator_id == created.operator.id
        assert created.first_mission_planner.operator_id == created.operator.id

    @pytest.mark.parametrize("name", ["operator", "cell_assignment", "first_mission_planner"])
    def test_none_is_refused_because_no_field_has_a_default(self, name: str) -> None:
        data = self.valid()
        data[name] = None
        with pytest.raises((ValidationError, ValueError)):
            OperatorCreated.model_validate(data)

    def test_rejects_a_cell_assignment_of_another_operator(self) -> None:
        data = self.valid()
        data["cell_assignment"] = self.assignment(self.OTHER_ID)
        with pytest.raises(SEOperatorCreatedForeignCellAssignment):
            OperatorCreated.model_validate(data)

    @pytest.mark.parametrize("operator_id", [OTHER_ID, None])
    def test_rejects_a_person_of_another_operator(self, operator_id: Optional[str]) -> None:
        data = self.valid()
        data["first_mission_planner"] = self.person(operator_id)
        with pytest.raises(SEOperatorCreatedForeignPerson):
            OperatorCreated.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            OperatorCreated.model_validate(data)

    def test_round_trip(self) -> None:
        created = OperatorCreated.model_validate(self.valid())
        assert OperatorCreated.model_validate(created.model_dump()) == created
        assert OperatorCreated.model_validate_json(created.model_dump_json()) == created
