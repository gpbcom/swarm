from __future__ import annotations

# Standard library imports
from typing import Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_models.operators.exceptions import SEOperatorDirectoryEntryForeignCellAssignment
from swarm_models.operators.operator import Operator
from swarm_models.operators.operator_directory_entry import OperatorDirectoryEntry


class TestOperatorDirectoryEntry:
    OPERATOR_ID: str = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    OTHER_ID: str = "01943c5e-8a4b-7d00-8000-000000000001"

    def operator(self) -> Dict[str, JsonValue]:
        return {
            "id": self.OPERATOR_ID,
            "name": "Aerowing Services",
            "deployment": "cloud",
            "jurisdictions": ["eu_easa"],
        }

    def assignment(self, operator_id: str) -> Dict[str, JsonValue]:
        return {"operator_id": operator_id, "cell": "cell-eu-1", "assigned_at": "2027-01-18T09:30:00+00:00"}

    def valid(self) -> Dict[str, JsonValue]:
        return {"operator": self.operator(), "cell_assignment": self.assignment(self.OPERATOR_ID)}

    def test_defaults(self) -> None:
        for name in ("operator", "cell_assignment"):
            assert OperatorDirectoryEntry.model_fields[name].is_required()

    def test_full_valid_construction(self) -> None:
        entry = OperatorDirectoryEntry.model_validate(self.valid())
        assert isinstance(entry.operator, Operator)
        assert isinstance(entry.cell_assignment, CellAssignment)
        assert entry.cell_assignment.operator_id == UUID(self.OPERATOR_ID)

    @pytest.mark.parametrize("name", ["operator", "cell_assignment"])
    def test_none_is_refused_because_no_field_has_a_default(self, name: str) -> None:
        data = self.valid()
        data[name] = None
        with pytest.raises((ValidationError, ValueError)):
            OperatorDirectoryEntry.model_validate(data)

    def test_rejects_a_cell_assignment_of_another_operator(self) -> None:
        data = self.valid()
        data["cell_assignment"] = self.assignment(self.OTHER_ID)
        with pytest.raises(SEOperatorDirectoryEntryForeignCellAssignment):
            OperatorDirectoryEntry.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            OperatorDirectoryEntry.model_validate(data)

    def test_round_trip(self) -> None:
        entry = OperatorDirectoryEntry.model_validate(self.valid())
        assert OperatorDirectoryEntry.model_validate(entry.model_dump()) == entry
        assert OperatorDirectoryEntry.model_validate_json(entry.model_dump_json()) == entry
