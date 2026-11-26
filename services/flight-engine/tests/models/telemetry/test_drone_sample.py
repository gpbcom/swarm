from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Tuple

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from flight_engine.models.telemetry.drone_sample import DroneSample
from flight_engine.models.telemetry.exceptions import (
    SEDroneSampleInvalidBaseMode,
    SEDroneSampleInvalidBatteryRemaining,
    SEDroneSampleInvalidHasPosition,
    SEDroneSampleInvalidHdgCdeg,
    SEDroneSampleInvalidLatE7,
    SEDroneSampleInvalidLonE7,
    SEDroneSampleInvalidLost,
    SEDroneSampleInvalidReceived,
    SEDroneSampleInvalidRelativeAltMm,
    SEDroneSampleInvalidSystemId,
    SEDroneSampleInvalidSystemStatus,
    SEDroneSampleInvalidUpdatedAtUs,
    SEDroneSampleInvalidVxCmS,
    SEDroneSampleInvalidVyCmS,
    SEInvalidDroneSampleException,
)


class TestDroneSample:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "system_id": 1,
        "has_position": True,
        "lat_e7": 473977418,
        "lon_e7": 85455938,
        "relative_alt_mm": 12000,
        "vx_cm_s": 150,
        "vy_cm_s": -20,
        "hdg_cdeg": 9000,
        "battery_remaining": 87,
        "base_mode": 209,
        "system_status": 4,
        "received": 42,
        "lost": 1,
        "updated_at_us": 1_500_000,
    }
    ERRORS: ClassVar[Dict[str, type[Exception]]] = {
        "system_id": SEDroneSampleInvalidSystemId,
        "has_position": SEDroneSampleInvalidHasPosition,
        "lat_e7": SEDroneSampleInvalidLatE7,
        "lon_e7": SEDroneSampleInvalidLonE7,
        "relative_alt_mm": SEDroneSampleInvalidRelativeAltMm,
        "vx_cm_s": SEDroneSampleInvalidVxCmS,
        "vy_cm_s": SEDroneSampleInvalidVyCmS,
        "hdg_cdeg": SEDroneSampleInvalidHdgCdeg,
        "battery_remaining": SEDroneSampleInvalidBatteryRemaining,
        "base_mode": SEDroneSampleInvalidBaseMode,
        "system_status": SEDroneSampleInvalidSystemStatus,
        "received": SEDroneSampleInvalidReceived,
        "lost": SEDroneSampleInvalidLost,
        "updated_at_us": SEDroneSampleInvalidUpdatedAtUs,
    }
    BOUNDED: ClassVar[List[Tuple[str, int, int]]] = [
        ("system_id", 1, 255),
        ("lat_e7", -(2**31), 2**31 - 1),
        ("lon_e7", -(2**31), 2**31 - 1),
        ("relative_alt_mm", -(2**31), 2**31 - 1),
        ("vx_cm_s", -(2**15), 2**15 - 1),
        ("vy_cm_s", -(2**15), 2**15 - 1),
        ("hdg_cdeg", 0, 2**16 - 1),
        ("battery_remaining", -1, 100),
        ("base_mode", 0, 255),
        ("system_status", 0, 255),
    ]
    NON_NEGATIVE: ClassVar[List[str]] = ["received", "lost", "updated_at_us"]
    NUMBERS: ClassVar[List[str]] = [name for name, _, _ in BOUNDED] + NON_NEGATIVE

    def build(self, **changes: JsonValue) -> DroneSample:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return DroneSample.model_validate(values)

    def test_defaults(self) -> None:
        sample = self.build()
        assert sample.system_id == 1
        assert sample.has_position is True

    def test_full_valid_construction(self) -> None:
        sample = self.build()
        for name, value in self.VALID.items():
            assert getattr(sample, name) == value

    @pytest.mark.parametrize("name", list(ERRORS))
    def test_none_is_refused_for_a_required_field(self, name: str) -> None:
        with pytest.raises(SEInvalidDroneSampleException):
            self.build(**{name: None})

    @pytest.mark.parametrize(("name", "low", "high"), BOUNDED)
    def test_a_value_past_the_bounds_of_its_integer_type_is_refused(self, name: str, low: int, high: int) -> None:
        with pytest.raises(self.ERRORS[name]):
            self.build(**{name: low - 1})
        with pytest.raises(self.ERRORS[name]):
            self.build(**{name: high + 1})

    @pytest.mark.parametrize(("name", "low", "high"), BOUNDED)
    def test_the_bounds_of_every_integer_type_are_accepted(self, name: str, low: int, high: int) -> None:
        assert getattr(self.build(**{name: low}), name) == low
        assert getattr(self.build(**{name: high}), name) == high

    @pytest.mark.parametrize("name", NON_NEGATIVE)
    def test_a_counter_or_a_time_below_zero_is_refused(self, name: str) -> None:
        with pytest.raises(self.ERRORS[name]):
            self.build(**{name: -1})

    @pytest.mark.parametrize("name", NON_NEGATIVE)
    def test_a_counter_or_a_time_of_zero_is_accepted(self, name: str) -> None:
        assert getattr(self.build(**{name: 0}), name) == 0

    @pytest.mark.parametrize("name", NUMBERS)
    @pytest.mark.parametrize("value", [True, 1.5, "1", [1]])
    def test_rejects_bools_and_other_types_for_numbers(self, name: str, value: JsonValue) -> None:
        with pytest.raises(self.ERRORS[name]):
            self.build(**{name: value})

    @pytest.mark.parametrize("value", [1, 0, "true", 1.0])
    def test_rejects_a_has_position_that_is_not_a_bool(self, value: JsonValue) -> None:
        with pytest.raises(SEDroneSampleInvalidHasPosition):
            self.build(has_position=value)

    def test_an_unknown_battery_is_minus_one(self) -> None:
        assert self.build(battery_remaining=-1).battery_remaining == -1

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(colour="red")

    def test_a_sample_cannot_change(self) -> None:
        sample = self.build()
        with pytest.raises(ValidationError):
            sample.lost = 2

    def test_round_trip(self) -> None:
        sample = self.build()
        assert DroneSample.model_validate(sample.model_dump()) == sample
        assert DroneSample.model_validate_json(sample.model_dump_json()) == sample

    @pytest.mark.parametrize("name", list(ERRORS))
    def test_the_field_exceptions_share_the_model_base(self, name: str) -> None:
        assert issubclass(self.ERRORS[name], SEInvalidDroneSampleException)
