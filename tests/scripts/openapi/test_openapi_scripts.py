from __future__ import annotations

# Standard library imports
from importlib.metadata import entry_points
from pathlib import Path
from typing import Callable, ClassVar, Dict

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import AppName
from swarm_scripts.openapi.check import main as check
from swarm_scripts.openapi.export import main as export
from swarm_scripts.repository_paths import RepositoryPaths
from swarm_scripts.swarm_apps import SwarmApps
from swarm_service.shared.openapi.openapi_exporter import OpenApiExporter


class TestOpenApiScripts:
    CONSOLE_SCRIPTS: ClassVar[Dict[str, str]] = {
        "swarm-openapi-export": "swarm_scripts.openapi.export:main",
        "swarm-openapi-check": "swarm_scripts.openapi.check:main",
    }
    OPENAPI_FOLDER: ClassVar[str] = "frontend/packages/api-client/openapi"
    ENCODING: ClassVar[str] = "utf-8"
    UNKNOWN_APP: ClassVar[str] = "nowhere"
    OPENAPI_ATTRIBUTE: ClassVar[str] = "OPENAPI"

    @pytest.fixture(autouse=True)
    def every_app(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(SwarmApps.APP_KEY, raising=False)

    @pytest.mark.parametrize(("name", "target"), list(CONSOLE_SCRIPTS.items()))
    def test_each_console_script_points_to_its_main(self, name: str, target: str) -> None:
        assert entry_points(group="console_scripts")[name].value == target

    def test_the_documents_are_those_of_the_api_client(self) -> None:
        assert RepositoryPaths.OPENAPI == RepositoryPaths.ROOT / self.OPENAPI_FOLDER
        assert RepositoryPaths.OPENAPI.is_dir()

    @pytest.mark.parametrize("app", list(AppName))
    def test_the_published_document_of_each_app_is_the_one_its_app_serves(self, app: AppName) -> None:
        exporter = OpenApiExporter(SwarmApps.APPLICATIONS[app](), RepositoryPaths.OPENAPI, app.value)

        assert exporter.path.is_file(), "Run `uv run swarm-openapi-export` to publish the document."
        assert exporter.is_stale() is False, "Run `uv run swarm-openapi-export`: the published document is stale."

    def test_the_check_passes_on_the_published_documents(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert check() == 0
        output = capsys.readouterr().out
        assert all(f"{app.value}.json is up to date" in output for app in AppName)

    def test_the_export_writes_the_published_documents(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        published = RepositoryPaths.OPENAPI
        monkeypatch.setattr(RepositoryPaths, self.OPENAPI_ATTRIBUTE, tmp_path)

        assert export() == 0
        for app in AppName:
            name = f"{app.value}.json"
            written = (tmp_path / name).read_text(encoding=self.ENCODING)
            assert written == (published / name).read_text(encoding=self.ENCODING)

    def test_the_app_entry_narrows_the_scripts_to_one_app(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv(SwarmApps.APP_KEY, AppName.FLEET.value)
        monkeypatch.setattr(RepositoryPaths, self.OPENAPI_ATTRIBUTE, tmp_path)

        assert export() == 0
        assert sorted(path.name for path in tmp_path.iterdir()) == [f"{AppName.FLEET.value}.json"]

    def test_a_stale_document_fails_the_check(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv(SwarmApps.APP_KEY, AppName.MISSIONS.value)
        monkeypatch.setattr(RepositoryPaths, self.OPENAPI_ATTRIBUTE, tmp_path)

        assert check() == 1

    @pytest.mark.parametrize("script", [export, check])
    def test_an_unknown_app_stops_the_scripts_with_two(
        self, monkeypatch: pytest.MonkeyPatch, script: Callable[[], int]
    ) -> None:
        monkeypatch.setenv(SwarmApps.APP_KEY, self.UNKNOWN_APP)

        assert script() == 2
