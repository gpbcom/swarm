from __future__ import annotations

# Standard library imports
from importlib.metadata import entry_points
from typing import ClassVar, Dict

# Third-party imports
import pytest

# First-party imports
from swarm_scripts.repository_paths import RepositoryPaths
from swarm_scripts.schemas.check import main as check
from swarm_service.shared.schema.schema_exporter import SchemaExporter


class TestSchemasScripts:
    CONSOLE_SCRIPTS: ClassVar[Dict[str, str]] = {
        "swarm-schemas-export": "swarm_scripts.schemas.export:main",
        "swarm-schemas-check": "swarm_scripts.schemas.check:main",
    }

    @pytest.mark.parametrize(("name", "target"), list(CONSOLE_SCRIPTS.items()))
    def test_each_console_script_points_to_its_main(self, name: str, target: str) -> None:
        assert entry_points(group="console_scripts")[name].value == target

    def test_the_bundle_folder_is_the_schemas_folder_of_swarm_models(self) -> None:
        assert RepositoryPaths.SCHEMAS.parts[-3:] == ("backend", "swarm-models", "schemas")
        assert RepositoryPaths.SCHEMAS.is_dir()

    def test_the_committed_bundle_is_up_to_date(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert check() == 0
        assert "is up to date" in capsys.readouterr().out

    def test_the_bundle_the_scripts_check_is_the_one_the_exporter_writes(self) -> None:
        assert SchemaExporter(RepositoryPaths.SCHEMAS).path == RepositoryPaths.SCHEMAS / SchemaExporter.FILE_NAME
