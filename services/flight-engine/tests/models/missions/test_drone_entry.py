from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from flight_engine.models.missions.drone_entry import DroneEntry
from flight_engine.models.missions.exceptions import (
    SEDroneEntryInvalidDroneId,
    SEDroneEntryInvalidSystemId,
    SEInvalidDroneEntryException,
)


class TestDroneEntry:
    DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    UUID4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    VALID: ClassVar[Dict[str, JsonValue]] = {"system_id": 7, "drone_id": DRONE_ID}
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}

    def build(self, **changes: JsonValue) -> DroneEntry:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return DroneEntry.model_validate(values)

    def test_defaults(self) -> None:
        entry = self.build()
        assert entry.system_id == 7
        assert entry.drone_id == UUID(self.DRONE_ID)

    def test_full_valid_construction(self) -> None:
        entry = self.build(system_id=255)
        assert entry.system_id == 255
        assert entry.drone_id == UUID(self.DRONE_ID)

    @pytest.mark.parametrize("name", ["system_id", "drone_id"])
    def test_none_is_refused_for_a_required_field(self, name: str) -> None:
        with pytest.raises(SEInvalidDroneEntryException):
            self.build(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("system_id", 0, SEDroneEntryInvalidSystemId),
            ("system_id", 256, SEDroneEntryInvalidSystemId),
            ("system_id", -1, SEDroneEntryInvalidSystemId),
            ("system_id", True, SEDroneEntryInvalidSystemId),
            ("system_id", 1.5, SEDroneEntryInvalidSystemId),
            ("system_id", "1", SEDroneEntryInvalidSystemId),
            ("drone_id", UUID4, SEDroneEntryInvalidDroneId),
            ("drone_id", "not-a-uuid", SEDroneEntryInvalidDroneId),
            ("drone_id", 7, SEDroneEntryInvalidDroneId),
            ("drone_id", True, SEDroneEntryInvalidDroneId),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            DroneEntry.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        entry = self.build()
        assert DroneEntry.model_validate(entry.model_dump()) == entry

    @pytest.mark.parametrize("system_id", [1, 255])
    def test_the_bounds_of_the_system_id_are_accepted(self, system_id: int) -> None:
        assert self.build(system_id=system_id).system_id == system_id

    @pytest.mark.parametrize("error", [SEDroneEntryInvalidSystemId, SEDroneEntryInvalidDroneId])
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidDroneEntryException)
