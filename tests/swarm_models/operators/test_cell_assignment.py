from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime, timedelta, timezone
from typing import Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_models.operators.exceptions import (
    SECellAssignmentInvalidAssignedAt,
    SECellAssignmentInvalidCell,
    SECellAssignmentInvalidOperatorId,
    SEInvalidCellAssignmentException,
)


class TestCellAssignment:
    VALID_ID: str = "01943c5e-8a4b-7d00-8000-000000000001"
    V4_ID: str = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"

    def valid(self) -> Dict[str, JsonValue]:
        return {
            "operator_id": self.VALID_ID,
            "cell": "  cell-eu-1  ",
            "assigned_at": "2027-01-18T09:30:00.123456+01:00",
        }

    def test_defaults(self) -> None:
        for name in ("operator_id", "cell", "assigned_at"):
            assert CellAssignment.model_fields[name].is_required()

    def test_full_valid_construction(self) -> None:
        assignment = CellAssignment.model_validate(self.valid())
        assert assignment.operator_id == UUID(self.VALID_ID)
        assert assignment.cell == "cell-eu-1"
        assert assignment.assigned_at == datetime(2027, 1, 18, 8, 30, 0, 123456, tzinfo=UTC)
        assert assignment.assigned_at.utcoffset() == timedelta(0)

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("operator_id", SECellAssignmentInvalidOperatorId),
            ("cell", SECellAssignmentInvalidCell),
            ("assigned_at", SECellAssignmentInvalidAssignedAt),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception]) -> None:
        """No field has a default, so None is refused with the exception of that field."""
        data = self.valid()
        data[name] = None
        with pytest.raises(error):
            CellAssignment.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("operator_id", V4_ID, SECellAssignmentInvalidOperatorId),
            ("operator_id", "not-a-uuid", SECellAssignmentInvalidOperatorId),
            ("operator_id", 7, SECellAssignmentInvalidOperatorId),
            ("operator_id", True, SECellAssignmentInvalidOperatorId),
            ("cell", "", SECellAssignmentInvalidCell),
            ("cell", "   ", SECellAssignmentInvalidCell),
            ("cell", 3, SECellAssignmentInvalidCell),
            ("assigned_at", "2027-01-18T09:30:00", SECellAssignmentInvalidAssignedAt),
            ("assigned_at", 1700000000, SECellAssignmentInvalidAssignedAt),
            ("assigned_at", True, SECellAssignmentInvalidAssignedAt),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(error):
            CellAssignment.model_validate(data)

    def test_a_naive_datetime_object_is_refused(self) -> None:
        with pytest.raises(SECellAssignmentInvalidAssignedAt):
            CellAssignment(
                operator_id=UUID(self.VALID_ID),
                cell="cell-eu-1",
                assigned_at=datetime(2027, 1, 18, 9, 30, 0),
            )

    def test_an_aware_datetime_object_is_converted_to_utc(self) -> None:
        assignment = CellAssignment(
            operator_id=UUID(self.VALID_ID),
            cell="cell-eu-1",
            assigned_at=datetime(2027, 1, 18, 9, 30, 0, tzinfo=timezone(timedelta(hours=1))),
        )
        assert assignment.assigned_at == datetime(2027, 1, 18, 8, 30, 0, tzinfo=UTC)
        assert assignment.assigned_at.utcoffset() == timedelta(0)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["extra"] = 1
        with pytest.raises(ValidationError):
            CellAssignment.model_validate(data)

    def test_round_trip(self) -> None:
        assignment = CellAssignment.model_validate(self.valid())
        assert CellAssignment.model_validate(assignment.model_dump()) == assignment
        assert CellAssignment.model_validate_json(assignment.model_dump_json()) == assignment

    @pytest.mark.parametrize(
        "error",
        [SECellAssignmentInvalidOperatorId, SECellAssignmentInvalidCell, SECellAssignmentInvalidAssignedAt],
    )
    def test_every_field_exception_belongs_to_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidCellAssignmentException)
        assert not issubclass(error, ValueError)
        assert not issubclass(SEInvalidCellAssignmentException, ValueError)
