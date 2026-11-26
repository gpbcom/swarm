from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
import yaml
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.flight.missions.exceptions import (
    SEMissionCatalogDuplicateMission,
    SEMissionCatalogDuplicatePort,
    SEMissionCatalogInvalidMissions,
    SEMissionCatalogUnreadable,
)
from swarm_models.flight.missions.mission_catalog import MissionCatalog


class TestMissionCatalog:
    SHIPPED: ClassVar[Path] = (
        Path(__file__).resolve().parents[4]
        / "backend"
        / "apps"
        / "flight-engine"
        / "conf"
        / "catalogs"
        / "missions.yaml"
    )
    OPERATOR_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5e"
    FIRST: ClassVar[Dict[str, JsonValue]] = {
        "operator_id": OPERATOR_ID,
        "mission_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f",
        "mavlink_port": 14550,
        "drones": [{"system_id": 1, "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61"}],
    }
    SECOND: ClassVar[Dict[str, JsonValue]] = {
        "operator_id": OPERATOR_ID,
        "mission_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e70",
        "mavlink_port": 14551,
        "drones": [{"system_id": 1, "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e71"}],
    }
    SAME_MISSION: ClassVar[Dict[str, JsonValue]] = {**SECOND, "mission_id": FIRST["mission_id"]}
    SAME_PORT: ClassVar[Dict[str, JsonValue]] = {**SECOND, "mavlink_port": FIRST["mavlink_port"]}
    VALID: ClassVar[Dict[str, JsonValue]] = {"missions": [FIRST, SECOND]}
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}
    NOT_A_MAPPING: ClassVar[List[str]] = ["missions"]

    def write(self, tmp_path: Path, content: JsonValue) -> Path:
        path = tmp_path / "missions.yaml"
        path.write_text(yaml.safe_dump(content), encoding="utf-8")
        return path

    def test_defaults(self) -> None:
        assert MissionCatalog().missions == []

    def test_full_valid_construction(self, tmp_path: Path) -> None:
        catalog = MissionCatalog.load(self.write(tmp_path, self.VALID))
        assert [mission.mavlink_port for mission in catalog.missions] == [14550, 14551]

    def test_none_becomes_the_default(self) -> None:
        assert MissionCatalog.model_validate({"missions": None}).missions == []

    @pytest.mark.parametrize("value", ["missions", 3, True, {"mission_id": "x"}, [3]])
    def test_rejects_bad_values(self, value: JsonValue) -> None:
        with pytest.raises(SEMissionCatalogInvalidMissions):
            MissionCatalog.model_validate({"missions": value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            MissionCatalog.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        catalog = MissionCatalog.model_validate(self.VALID)
        assert MissionCatalog.model_validate(catalog.model_dump()) == catalog

    def test_a_duplicate_mission_id_is_refused(self) -> None:
        with pytest.raises(SEMissionCatalogDuplicateMission):
            MissionCatalog.model_validate({"missions": [self.FIRST, self.SAME_MISSION]})

    def test_a_duplicate_mavlink_port_is_refused(self) -> None:
        with pytest.raises(SEMissionCatalogDuplicatePort):
            MissionCatalog.model_validate({"missions": [self.FIRST, self.SAME_PORT]})

    def test_the_same_system_id_in_two_missions_is_accepted(self) -> None:
        assert len(MissionCatalog.model_validate(self.VALID).missions) == 2

    def test_the_unreadable_error_is_the_one_of_load(self) -> None:
        assert MissionCatalog.UNREADABLE is SEMissionCatalogUnreadable

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SEMissionCatalogUnreadable):
            MissionCatalog.load(tmp_path / "missing.yaml")

    def test_a_file_that_is_not_a_mapping_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SEMissionCatalogUnreadable):
            MissionCatalog.load(self.write(tmp_path, self.NOT_A_MAPPING))

    def test_the_shipped_catalog_holds_no_mission(self) -> None:
        assert MissionCatalog.load(self.SHIPPED).missions == []
