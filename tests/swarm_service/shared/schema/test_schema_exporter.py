from __future__ import annotations

# Standard library imports
import json
import logging
from pathlib import Path
from typing import List

# Third-party imports
import pytest

# First-party imports
from swarm_models.commands.command import Command
from swarm_models.events.actor import Actor
from swarm_models.events.event import Event
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_models.operators.operator import Operator
from swarm_models.people.person import Person
from swarm_models.people.role import Role
from swarm_models.telemetry.squad_frame import SquadFrame
from swarm_models.telemetry.telemetry_frame import TelemetryFrame
from swarm_service.shared.schema.schema_exporter import SchemaExporter
from swarm_storage.shared.schemas.schema_folder import SchemaFolder


class TestSchemaExporter:
    EXPECTED_DEFS = (
        "Operator",
        "CellAssignment",
        "Person",
        "Role",
        "RoleName",
        "Actor",
        "ActorKind",
        "Event",
        "TelemetryFrame",
        "DroneState",
        "SquadFrame",
        "Command",
        "CommandKind",
        "CommandLane",
        "LiveSubscription",
        "LiveOperation",
        "LiveRate",
    )
    TELEMETRY_FIELDS = (
        "mission_id",
        "drone_id",
        "seq",
        "t_us",
        "lat_e7",
        "lon_e7",
        "altitude_m",
        "speed_m_s",
        "heading_deg",
        "battery_pct",
        "link_quality_pct",
        "state",
    )

    def test_the_models_are_the_ten_in_order(self) -> None:
        assert SchemaExporter.MODELS == (
            Operator,
            CellAssignment,
            Person,
            Role,
            Actor,
            Event,
            TelemetryFrame,
            SquadFrame,
            Command,
            LiveSubscription,
        )

    def test_the_file_name_and_the_title_are_fixed(self) -> None:
        assert SchemaExporter.FILE_NAME == "swarm_models.schema.json"
        assert SchemaExporter.TITLE == "Swarm models"

    def test_the_folder_is_rooted_at_the_given_root(self, tmp_path: Path) -> None:
        exporter = SchemaExporter(root=tmp_path)
        assert isinstance(exporter.folder, SchemaFolder)
        assert exporter.folder.root == tmp_path

    def test_the_path_is_the_file_name_under_the_root(self, tmp_path: Path) -> None:
        assert SchemaExporter(root=tmp_path).path == tmp_path / "swarm_models.schema.json"

    def test_render_has_only_the_defs_and_the_title(self, tmp_path: Path) -> None:
        bundle = json.loads(SchemaExporter(root=tmp_path).render())
        assert sorted(bundle.keys()) == ["$defs", "title"]
        assert bundle["title"] == "Swarm models"

    def test_render_holds_the_eighteen_definitions(self, tmp_path: Path) -> None:
        defs = json.loads(SchemaExporter(root=tmp_path).render())["$defs"]
        assert set(self.EXPECTED_DEFS) <= set(defs.keys())

    def test_render_describes_the_twelve_telemetry_fields(self, tmp_path: Path) -> None:
        defs = json.loads(SchemaExporter(root=tmp_path).render())["$defs"]
        assert set(defs["TelemetryFrame"]["properties"].keys()) == set(self.TELEMETRY_FIELDS)

    def test_render_is_identical_across_calls(self, tmp_path: Path) -> None:
        exporter = SchemaExporter(root=tmp_path)
        assert exporter.render() == exporter.render()

    def test_render_ends_with_one_newline(self, tmp_path: Path) -> None:
        text = SchemaExporter(root=tmp_path).render()
        assert text.endswith("}\n")
        assert not text.endswith("\n\n")

    def test_render_equals_its_canonical_re_dump(self, tmp_path: Path) -> None:
        text = SchemaExporter(root=tmp_path).render()
        redump = json.dumps(json.loads(text), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        assert text == redump

    def test_export_writes_the_rendered_text_and_returns_the_path(self, tmp_path: Path) -> None:
        exporter = SchemaExporter(root=tmp_path)
        written = exporter.export()
        assert written == tmp_path / "swarm_models.schema.json"
        assert written.read_text(encoding="utf-8") == exporter.render()

    def test_a_bundle_is_stale_before_the_export(self, tmp_path: Path) -> None:
        assert SchemaExporter(root=tmp_path).is_stale() is True

    def test_a_bundle_is_fresh_after_the_export(self, tmp_path: Path) -> None:
        exporter = SchemaExporter(root=tmp_path)
        exporter.export()
        assert exporter.is_stale() is False

    def test_a_bundle_with_one_character_changed_is_stale(self, tmp_path: Path) -> None:
        exporter = SchemaExporter(root=tmp_path)
        path = exporter.export()
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("Swarm models", "Swarm modelz", 1), encoding="utf-8")
        assert exporter.is_stale() is True

    def test_a_bundle_with_a_trailing_space_is_stale(self, tmp_path: Path) -> None:
        exporter = SchemaExporter(root=tmp_path)
        path = exporter.export()
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        assert exporter.is_stale() is True

    def test_the_export_logs_at_info(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        exporter = SchemaExporter(root=tmp_path, logger=logging.getLogger("test.schema_exporter"))
        with caplog.at_level(logging.DEBUG, logger="test.schema_exporter"):
            exporter.export()
        levels: List[int] = [record.levelno for record in caplog.records]
        assert logging.INFO in levels

    def test_a_stale_bundle_logs_a_warning_and_a_fresh_one_does_not(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        exporter = SchemaExporter(root=tmp_path, logger=logging.getLogger("test.schema_exporter"))
        with caplog.at_level(logging.DEBUG, logger="test.schema_exporter"):
            exporter.is_stale()
        assert logging.WARNING in [record.levelno for record in caplog.records]
        exporter.export()
        caplog.clear()
        with caplog.at_level(logging.DEBUG, logger="test.schema_exporter"):
            exporter.is_stale()
        assert logging.WARNING not in [record.levelno for record in caplog.records]
