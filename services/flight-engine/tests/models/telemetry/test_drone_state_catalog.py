from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue, ValidationError

# First-party imports
from flight_engine.models.telemetry.drone_state_catalog import DroneStateCatalog
from flight_engine.models.telemetry.exceptions import (
    SEDroneStateCatalogInvalidDefaultState,
    SEDroneStateCatalogInvalidSystemStatusStates,
    SEDroneStateCatalogUnreadable,
)
from swarm_models.telemetry.enums import DroneState


class TestDroneStateCatalog:
    SHIPPED: ClassVar[Path] = Path(__file__).resolve().parents[3] / "conf" / "catalogs" / "drone_states.yaml"
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "system_status_states": {3: DroneState.READY.value, 4: DroneState.AIRBORNE.value},
        "default_state": DroneState.LANDED.value,
    }
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}
    NOT_A_MAPPING: ClassVar[List[str]] = ["system_status_states"]

    def write(self, tmp_path: Path, content: JsonValue) -> Path:
        path = tmp_path / "drone_states.yaml"
        path.write_text(yaml.safe_dump(content), encoding="utf-8")
        return path

    def test_defaults(self) -> None:
        assert DroneStateCatalog().default_state == DroneState.GROUNDED

    def test_full_valid_construction(self, tmp_path: Path) -> None:
        catalog = DroneStateCatalog.load(self.write(tmp_path, self.VALID))
        assert catalog.system_status_states == {3: DroneState.READY, 4: DroneState.AIRBORNE}
        assert catalog.default_state == DroneState.LANDED

    def test_none_becomes_the_default(self) -> None:
        assert DroneStateCatalog.model_validate({"default_state": None}).default_state == DroneState.GROUNDED

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("system_status_states", "ready", SEDroneStateCatalogInvalidSystemStatusStates),
            ("system_status_states", 3, SEDroneStateCatalogInvalidSystemStatusStates),
            ("system_status_states", [3], SEDroneStateCatalogInvalidSystemStatusStates),
            ("system_status_states", {"x": DroneState.READY.value}, SEDroneStateCatalogInvalidSystemStatusStates),
            ("system_status_states", {True: DroneState.READY.value}, SEDroneStateCatalogInvalidSystemStatusStates),
            ("system_status_states", {3: "teleporting"}, SEDroneStateCatalogInvalidSystemStatusStates),
            ("system_status_states", {3: 4}, SEDroneStateCatalogInvalidSystemStatusStates),
            ("default_state", "teleporting", SEDroneStateCatalogInvalidDefaultState),
            ("default_state", 3, SEDroneStateCatalogInvalidDefaultState),
            ("default_state", True, SEDroneStateCatalogInvalidDefaultState),
            ("default_state", "", SEDroneStateCatalogInvalidDefaultState),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            DroneStateCatalog.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            DroneStateCatalog.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        catalog = DroneStateCatalog.model_validate(self.VALID)
        assert DroneStateCatalog.model_validate(catalog.model_dump()) == catalog

    def test_a_listed_system_status_gives_its_state(self) -> None:
        catalog = DroneStateCatalog.model_validate(self.VALID)
        assert catalog.state_of(3) == DroneState.READY
        assert catalog.state_of(4) == DroneState.AIRBORNE

    def test_an_unlisted_system_status_gives_the_default_state(self) -> None:
        assert DroneStateCatalog.model_validate(self.VALID).state_of(0) == DroneState.LANDED

    def test_the_unreadable_error_is_the_one_of_load(self) -> None:
        assert DroneStateCatalog.UNREADABLE is SEDroneStateCatalogUnreadable

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SEDroneStateCatalogUnreadable):
            DroneStateCatalog.load(tmp_path / "missing.yaml")

    def test_a_file_that_is_not_a_mapping_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SEDroneStateCatalogUnreadable):
            DroneStateCatalog.load(self.write(tmp_path, self.NOT_A_MAPPING))

    def test_the_shipped_catalog_maps_the_mavlink_system_statuses(self) -> None:
        catalog = DroneStateCatalog.load(self.SHIPPED)
        assert catalog.default_state == DroneState.GROUNDED
        assert catalog.state_of(3) == DroneState.READY
        for system_status in (4, 5, 6):
            assert catalog.state_of(system_status) == DroneState.AIRBORNE
        assert catalog.state_of(0) == DroneState.GROUNDED
