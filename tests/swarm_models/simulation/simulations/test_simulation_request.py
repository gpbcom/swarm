from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.simulation.simulations.exceptions import SESimulationRequestInvalidMissionId
from swarm_models.simulation.simulations.simulation_request import SimulationRequest


class TestSimulationRequest:
    MISSION_ID: ClassVar[str] = "0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7d"
    UUID4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    CTX_KEY: ClassVar[str] = "ctx"
    ERROR_KEY: ClassVar[str] = "error"
    VALID: ClassVar[Dict[str, JsonValue]] = {"mission_id": MISSION_ID}

    def build(self, **changes: JsonValue) -> SimulationRequest:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return SimulationRequest.model_validate(values)

    def test_defaults(self) -> None:
        with pytest.raises(ValidationError):
            SimulationRequest.model_validate({})

    def test_full_valid_construction(self) -> None:
        assert self.build().mission_id == UUID(self.MISSION_ID)

    @pytest.mark.parametrize("name", ["mission_id"])
    def test_none_becomes_the_default(self, name: str) -> None:
        with pytest.raises(ValidationError):
            self.build(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("mission_id", UUID4, SESimulationRequestInvalidMissionId),
            ("mission_id", "not-a-uuid", SESimulationRequestInvalidMissionId),
            ("mission_id", 7, SESimulationRequestInvalidMissionId),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(ValidationError) as raised:
            self.build(**{name: value})

        assert isinstance(raised.value.errors()[0][self.CTX_KEY][self.ERROR_KEY], error)

    def test_a_refused_value_is_a_value_error_so_that_the_api_answers_422(self) -> None:
        assert issubclass(SESimulationRequestInvalidMissionId, ValueError)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(unknown=1)

    def test_round_trip(self) -> None:
        request = self.build()

        assert SimulationRequest.model_validate_json(request.model_dump_json()) == request
