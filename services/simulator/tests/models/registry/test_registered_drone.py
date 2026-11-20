from __future__ import annotations

from typing import ClassVar, Dict, List
from uuid import UUID

import pytest
from pydantic import JsonValue, ValidationError

from simulator.models.enums import SimulatedDroneKind
from simulator.models.registry.exceptions import (
    SERegisteredDroneInvalidDroneId,
    SERegisteredDroneInvalidHost,
    SERegisteredDroneInvalidKind,
    SERegisteredDroneInvalidPort,
    SERegisteredDroneInvalidSystemId,
)
from simulator.models.registry.registered_drone import RegisteredDrone


class TestRegisteredDrone:
    DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    VERSION_4_ID: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-8e7f-9a0b1c2d3e4f"
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "drone_id": DRONE_ID,
        "kind": SimulatedDroneKind.SYNTHETIC.value,
        "host": "synthetic-drones",
        "port": 14600,
        "system_id": 1,
    }
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SERegisteredDroneInvalidDroneId,
        SERegisteredDroneInvalidKind,
        SERegisteredDroneInvalidHost,
        SERegisteredDroneInvalidPort,
        SERegisteredDroneInvalidSystemId,
    ]

    def test_defaults(self) -> None:
        drone = RegisteredDrone.model_validate(self.VALID)
        assert drone.kind == SimulatedDroneKind.SYNTHETIC
        assert drone.drone_id.version == 7

    def test_full_valid_construction(self) -> None:
        drone = RegisteredDrone(
            drone_id=UUID(self.DRONE_ID),
            kind=SimulatedDroneKind.PX4_SITL,
            host="px4-sitl",
            port=18570,
            system_id=255,
        )
        assert drone.drone_id == UUID(self.DRONE_ID)
        assert drone.kind == SimulatedDroneKind.PX4_SITL
        assert drone.host == "px4-sitl"
        assert drone.port == 18570
        assert drone.system_id == 255

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("drone_id", SERegisteredDroneInvalidDroneId),
            ("kind", SERegisteredDroneInvalidKind),
            ("host", SERegisteredDroneInvalidHost),
            ("port", SERegisteredDroneInvalidPort),
            ("system_id", SERegisteredDroneInvalidSystemId),
        ],
    )
    def test_none_is_refused_because_no_field_has_a_default(self, name: str, error: type[Exception]) -> None:
        with pytest.raises(error):
            RegisteredDrone.model_validate({**self.VALID, name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("drone_id", "not-a-uuid", SERegisteredDroneInvalidDroneId),
            ("drone_id", VERSION_4_ID, SERegisteredDroneInvalidDroneId),
            ("drone_id", 3, SERegisteredDroneInvalidDroneId),
            ("kind", "real", SERegisteredDroneInvalidKind),
            ("kind", "", SERegisteredDroneInvalidKind),
            ("kind", 3, SERegisteredDroneInvalidKind),
            ("host", "", SERegisteredDroneInvalidHost),
            ("host", "   ", SERegisteredDroneInvalidHost),
            ("host", 3, SERegisteredDroneInvalidHost),
            ("port", 0, SERegisteredDroneInvalidPort),
            ("port", 65536, SERegisteredDroneInvalidPort),
            ("port", True, SERegisteredDroneInvalidPort),
            ("port", 1.5, SERegisteredDroneInvalidPort),
            ("port", "14600", SERegisteredDroneInvalidPort),
            ("system_id", 0, SERegisteredDroneInvalidSystemId),
            ("system_id", 256, SERegisteredDroneInvalidSystemId),
            ("system_id", True, SERegisteredDroneInvalidSystemId),
            ("system_id", 1.5, SERegisteredDroneInvalidSystemId),
            ("system_id", "1", SERegisteredDroneInvalidSystemId),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            RegisteredDrone.model_validate({**self.VALID, name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            RegisteredDrone.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        drone = RegisteredDrone.model_validate(self.VALID)
        assert RegisteredDrone.model_validate(drone.model_dump()) == drone
        assert RegisteredDrone.model_validate_json(drone.model_dump_json()) == drone

    @pytest.mark.parametrize(("port", "system_id"), [(1, 1), (65535, 255)])
    def test_the_bounds_are_accepted(self, port: int, system_id: int) -> None:
        drone = RegisteredDrone.model_validate({**self.VALID, "port": port, "system_id": system_id})
        assert drone.port == port
        assert drone.system_id == system_id

    def test_the_host_is_stripped(self) -> None:
        drone = RegisteredDrone.model_validate({**self.VALID, "host": "  px4-sitl "})
        assert drone.host == "px4-sitl"

    def test_a_drone_is_frozen(self) -> None:
        drone = RegisteredDrone.model_validate(self.VALID)
        with pytest.raises(ValidationError):
            drone.port = 14601

    def test_the_kinds_are_all_simulated(self) -> None:
        assert {kind.value for kind in SimulatedDroneKind} == {"synthetic", "px4_sitl"}

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_are_not_value_errors(self, error: type[Exception]) -> None:
        assert not issubclass(error, ValueError)
