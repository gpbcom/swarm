from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List
from uuid import UUID

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import SimulatedDroneKind
from swarm_models.simulation.registry.exceptions import (
    SESimulatedSquadCatalogDuplicateDrone,
    SESimulatedSquadCatalogDuplicateEndpoint,
    SESimulatedSquadCatalogInvalidDrones,
    SESimulatedSquadCatalogUnreadable,
)
from swarm_models.simulation.registry.simulated_squad_catalog import SimulatedSquadCatalog


class TestSimulatedSquadCatalog:
    SHIPPED: ClassVar[Path] = (
        Path(__file__).resolve().parents[4]
        / "backend"
        / "apps"
        / "simulator"
        / "conf"
        / "catalogs"
        / "simulated_squad.yaml"
    )
    FIRST: ClassVar[Dict[str, JsonValue]] = {
        "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e51",
        "kind": SimulatedDroneKind.SYNTHETIC.value,
        "host": "synthetic-drones",
        "port": 14600,
        "system_id": 1,
    }
    SECOND: ClassVar[Dict[str, JsonValue]] = {
        "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e52",
        "kind": SimulatedDroneKind.PX4_SITL.value,
        "host": "px4-sitl",
        "port": 18570,
        "system_id": 1,
    }
    SAME_DRONE: ClassVar[Dict[str, JsonValue]] = {**SECOND, "drone_id": FIRST["drone_id"]}
    SAME_ENDPOINT: ClassVar[Dict[str, JsonValue]] = {**SECOND, "host": FIRST["host"], "port": FIRST["port"]}
    OTHER_PORT: ClassVar[Dict[str, JsonValue]] = {**SAME_ENDPOINT, "port": 14601}
    VALID: ClassVar[Dict[str, JsonValue]] = {"drones": [FIRST, SECOND]}
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}
    NOT_A_MAPPING: ClassVar[List[str]] = ["drones"]

    def write(self, tmp_path: Path, content: JsonValue) -> Path:
        path = tmp_path / "simulated_squad.yaml"
        path.write_text(yaml.safe_dump(content), encoding="utf-8")
        return path

    def test_defaults(self) -> None:
        catalog = SimulatedSquadCatalog.model_validate(self.VALID)
        assert len(catalog.drones) == 2
        assert catalog.drones[0].drone_id == UUID(str(self.FIRST["drone_id"]))

    def test_full_valid_construction(self, tmp_path: Path) -> None:
        catalog = SimulatedSquadCatalog.load(self.write(tmp_path, self.VALID))
        assert [drone.kind for drone in catalog.drones] == [SimulatedDroneKind.SYNTHETIC, SimulatedDroneKind.PX4_SITL]

    def test_none_is_refused(self) -> None:
        with pytest.raises(SESimulatedSquadCatalogInvalidDrones):
            SimulatedSquadCatalog.model_validate({"drones": None})

    @pytest.mark.parametrize("value", [None, [], "drone", 3])
    def test_rejects_bad_values(self, value: JsonValue) -> None:
        with pytest.raises(SESimulatedSquadCatalogInvalidDrones):
            SimulatedSquadCatalog.model_validate({"drones": value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            SimulatedSquadCatalog.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        catalog = SimulatedSquadCatalog.model_validate(self.VALID)
        assert SimulatedSquadCatalog.model_validate(catalog.model_dump()) == catalog

    def test_a_duplicate_drone_id_is_refused(self) -> None:
        with pytest.raises(SESimulatedSquadCatalogDuplicateDrone):
            SimulatedSquadCatalog.model_validate({"drones": [self.FIRST, self.SAME_DRONE]})

    def test_a_duplicate_host_and_port_is_refused(self) -> None:
        with pytest.raises(SESimulatedSquadCatalogDuplicateEndpoint):
            SimulatedSquadCatalog.model_validate({"drones": [self.FIRST, self.SAME_ENDPOINT]})

    def test_the_same_host_on_another_port_is_accepted(self) -> None:
        catalog = SimulatedSquadCatalog.model_validate({"drones": [self.FIRST, self.OTHER_PORT]})
        assert len(catalog.drones) == 2

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SESimulatedSquadCatalogUnreadable):
            SimulatedSquadCatalog.load(tmp_path / "missing.yaml")

    def test_a_file_that_is_not_a_mapping_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SESimulatedSquadCatalogUnreadable):
            SimulatedSquadCatalog.load(self.write(tmp_path, self.NOT_A_MAPPING))

    def test_the_unreadable_exception_is_set(self) -> None:
        assert SimulatedSquadCatalog.UNREADABLE is SESimulatedSquadCatalogUnreadable

    def test_the_shipped_catalog_holds_eleven_drones(self) -> None:
        catalog = SimulatedSquadCatalog.load(self.SHIPPED)
        assert len(catalog.drones) == 11

    def test_the_shipped_synthetic_drones_are_on_ten_ports(self) -> None:
        catalog = SimulatedSquadCatalog.load(self.SHIPPED)
        synthetic = [drone for drone in catalog.drones if drone.kind == SimulatedDroneKind.SYNTHETIC]
        assert len(synthetic) == 10
        assert {drone.host for drone in synthetic} == {"synthetic-drones"}
        assert sorted(drone.port for drone in synthetic) == list(range(14600, 14610))
        assert sorted(drone.system_id for drone in synthetic) == list(range(1, 11))

    def test_the_shipped_px4_sitl_drone_is_registered(self) -> None:
        catalog = SimulatedSquadCatalog.load(self.SHIPPED)
        sitl = [drone for drone in catalog.drones if drone.kind == SimulatedDroneKind.PX4_SITL]
        assert len(sitl) == 1
        assert sitl[0].host == "px4-sitl"
        assert sitl[0].port == 18570
        assert sitl[0].system_id == 1
