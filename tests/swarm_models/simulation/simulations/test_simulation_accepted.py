from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.simulation.simulations.exceptions import (
    SESimulationAcceptedInvalidDroneIds,
    SESimulationAcceptedInvalidMissionId,
    SESimulationRunningError,
)
from swarm_models.simulation.simulations.simulation_accepted import SimulationAccepted
from swarm_web.models.rest.exceptions import SERestError


class TestSimulationAccepted:
    MISSION_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7d"
    DRONE_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-000000000101"
    UUID4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    VALID: ClassVar[Dict[str, JsonValue]] = {"mission_id": MISSION_ID, "drone_ids": [DRONE_ID]}

    def build(self, **changes: JsonValue) -> SimulationAccepted:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return SimulationAccepted.model_validate(values)

    def test_defaults(self) -> None:
        with pytest.raises(ValidationError):
            SimulationAccepted.model_validate({})

    def test_full_valid_construction(self) -> None:
        accepted = self.build()

        assert accepted.mission_id == UUID(self.MISSION_ID)
        assert accepted.drone_ids == [UUID(self.DRONE_ID)]

    @pytest.mark.parametrize(
        ("name", "error"),
        [("mission_id", SESimulationAcceptedInvalidMissionId), ("drone_ids", SESimulationAcceptedInvalidDroneIds)],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("mission_id", UUID4, SESimulationAcceptedInvalidMissionId),
            ("mission_id", "not-a-uuid", SESimulationAcceptedInvalidMissionId),
            ("drone_ids", DRONE_ID, SESimulationAcceptedInvalidDroneIds),
            ("drone_ids", [UUID4], SESimulationAcceptedInvalidDroneIds),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(unknown=1)

    def test_round_trip(self) -> None:
        accepted = self.build()

        assert SimulationAccepted.model_validate_json(accepted.model_dump_json()) == accepted

    def test_a_flight_that_flies_is_answered_with_a_conflict(self) -> None:
        assert issubclass(SESimulationRunningError, SERestError)
        assert SESimulationRunningError.STATUS == HTTPStatus.CONFLICT
