from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import SimulatedDroneKind
from swarm_models.simulation.flights.exceptions import (
    SEFlightOutcomeInvalidCompleted,
    SEFlightOutcomeInvalidDroneId,
    SEFlightOutcomeInvalidElapsed,
    SEFlightOutcomeInvalidKind,
    SEFlightOutcomeInvalidWaypointsReached,
)
from swarm_models.simulation.flights.flight_outcome import FlightOutcome


class TestFlightOutcome:
    DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    UUID4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "drone_id": DRONE_ID,
        "kind": SimulatedDroneKind.SYNTHETIC.value,
        "completed": True,
        "waypoints_reached": 4,
        "elapsed_s": 12.5,
    }

    def build(self, **changes: JsonValue) -> FlightOutcome:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return FlightOutcome.model_validate(values)

    def test_defaults(self) -> None:
        with pytest.raises(ValidationError):
            FlightOutcome.model_validate({})

    def test_full_valid_construction(self) -> None:
        outcome = self.build(kind=SimulatedDroneKind.PX4_SITL.value, completed=False)
        assert str(outcome.drone_id) == self.DRONE_ID
        assert outcome.kind == SimulatedDroneKind.PX4_SITL
        assert outcome.completed is False
        assert outcome.waypoints_reached == 4
        assert outcome.elapsed_s == 12.5

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("drone_id", SEFlightOutcomeInvalidDroneId),
            ("kind", SEFlightOutcomeInvalidKind),
            ("completed", SEFlightOutcomeInvalidCompleted),
            ("waypoints_reached", SEFlightOutcomeInvalidWaypointsReached),
            ("elapsed_s", SEFlightOutcomeInvalidElapsed),
        ],
    )
    def test_none_is_refused_as_no_field_has_a_default(self, name: str, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("drone_id", UUID4, SEFlightOutcomeInvalidDroneId),
            ("drone_id", "not-a-uuid", SEFlightOutcomeInvalidDroneId),
            ("drone_id", 7, SEFlightOutcomeInvalidDroneId),
            ("kind", "teleport", SEFlightOutcomeInvalidKind),
            ("kind", 3, SEFlightOutcomeInvalidKind),
            ("completed", 1, SEFlightOutcomeInvalidCompleted),
            ("completed", 0, SEFlightOutcomeInvalidCompleted),
            ("completed", "yes", SEFlightOutcomeInvalidCompleted),
            ("waypoints_reached", -1, SEFlightOutcomeInvalidWaypointsReached),
            ("waypoints_reached", True, SEFlightOutcomeInvalidWaypointsReached),
            ("waypoints_reached", 1.5, SEFlightOutcomeInvalidWaypointsReached),
            ("waypoints_reached", "1", SEFlightOutcomeInvalidWaypointsReached),
            ("elapsed_s", -0.1, SEFlightOutcomeInvalidElapsed),
            ("elapsed_s", True, SEFlightOutcomeInvalidElapsed),
            ("elapsed_s", float("nan"), SEFlightOutcomeInvalidElapsed),
            ("elapsed_s", "1.5", SEFlightOutcomeInvalidElapsed),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize("kind", list(SimulatedDroneKind))
    def test_every_kind_is_accepted_as_a_member_or_as_its_value(self, kind: SimulatedDroneKind) -> None:
        assert self.build(kind=kind.value).kind == kind
        assert self.build(kind=kind).kind == kind

    def test_zero_waypoints_and_zero_seconds_are_accepted(self) -> None:
        outcome = self.build(waypoints_reached=0, elapsed_s=0)
        assert outcome.waypoints_reached == 0
        assert outcome.elapsed_s == 0.0

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_outcome_is_refused(self) -> None:
        outcome = self.build()
        with pytest.raises(ValidationError):
            outcome.completed = False

    def test_round_trip(self) -> None:
        outcome = self.build()
        assert FlightOutcome.model_validate(outcome.model_dump()) == outcome
        assert FlightOutcome.model_validate_json(outcome.model_dump_json()) == outcome
