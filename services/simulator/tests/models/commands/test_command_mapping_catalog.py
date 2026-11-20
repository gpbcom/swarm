from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Dict, List

import pytest
import yaml
from pydantic import JsonValue, ValidationError

from simulator.models.commands.command_mapping_catalog import CommandMappingCatalog
from simulator.models.commands.exceptions import (
    SECommandMappingCatalogInvalidCommands,
    SECommandMappingCatalogUnreadable,
)
from swarm_models.models.commands.enums import CommandKind


class TestCommandMappingCatalog:
    SHIPPED: ClassVar[Path] = Path(__file__).parents[3] / "conf" / "catalogs" / "command_mapping.yaml"
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "commands": {
            CommandKind.HOLD.value: {"command_id": 193, "param1": 0.0},
            CommandKind.RETURN_HOME.value: {"command_id": 20},
        }
    }
    UNKNOWN_KIND: ClassVar[Dict[str, JsonValue]] = {"commands": {"dance": {"command_id": 1}}}
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}
    NOT_A_MAPPING: ClassVar[List[str]] = ["hold", "return_home"]

    def write(self, tmp_path: Path, content: JsonValue) -> Path:
        path = tmp_path / "command_mapping.yaml"
        path.write_text(yaml.safe_dump(content), encoding="utf-8")
        return path

    def test_defaults(self) -> None:
        catalog = CommandMappingCatalog.model_validate(self.VALID)
        assert set(catalog.commands) == {CommandKind.HOLD, CommandKind.RETURN_HOME}
        assert catalog.commands[CommandKind.RETURN_HOME].param1 == 0.0

    def test_full_valid_construction(self, tmp_path: Path) -> None:
        catalog = CommandMappingCatalog.load(self.write(tmp_path, self.VALID))
        assert catalog.commands[CommandKind.HOLD].command_id == 193
        assert catalog.commands[CommandKind.RETURN_HOME].command_id == 20

    def test_none_is_refused(self) -> None:
        with pytest.raises(SECommandMappingCatalogInvalidCommands):
            CommandMappingCatalog.model_validate({"commands": None})

    @pytest.mark.parametrize("value", [None, "hold", 3, ["hold"], {"dance": {"command_id": 1}}])
    def test_rejects_bad_values(self, value: JsonValue) -> None:
        with pytest.raises(SECommandMappingCatalogInvalidCommands):
            CommandMappingCatalog.model_validate({"commands": value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            CommandMappingCatalog.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        catalog = CommandMappingCatalog.model_validate(self.VALID)
        assert CommandMappingCatalog.model_validate(catalog.model_dump()) == catalog

    def test_an_unknown_command_kind_is_refused_from_a_file(self, tmp_path: Path) -> None:
        with pytest.raises(SECommandMappingCatalogInvalidCommands):
            CommandMappingCatalog.load(self.write(tmp_path, self.UNKNOWN_KIND))

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SECommandMappingCatalogUnreadable):
            CommandMappingCatalog.load(tmp_path / "missing.yaml")

    def test_a_file_that_is_not_a_mapping_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SECommandMappingCatalogUnreadable):
            CommandMappingCatalog.load(self.write(tmp_path, self.NOT_A_MAPPING))

    def test_the_unreadable_exception_is_set(self) -> None:
        assert CommandMappingCatalog.UNREADABLE is SECommandMappingCatalogUnreadable

    def test_the_shipped_catalog_maps_hold_and_return_home(self) -> None:
        catalog = CommandMappingCatalog.load(self.SHIPPED)
        hold = catalog.commands[CommandKind.HOLD]
        assert hold.command_id == 193
        assert hold.param1 == 0.0
        assert catalog.commands[CommandKind.RETURN_HOME].command_id == 20

    @pytest.mark.parametrize("kind", [CommandKind.ABORT, CommandKind.MANUAL_CONTROL])
    def test_the_shipped_catalog_leaves_out_abort_and_manual_control(self, kind: CommandKind) -> None:
        catalog = CommandMappingCatalog.load(self.SHIPPED)
        assert kind not in catalog.commands
