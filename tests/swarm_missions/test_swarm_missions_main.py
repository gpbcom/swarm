from __future__ import annotations

# Standard library imports
from importlib.metadata import entry_points
from inspect import signature
from pathlib import Path
from typing import ClassVar

# Third-party imports
import httpx

# First-party imports
from swarm_api.v1.missions.missions_router import MissionsRouter
from swarm_missions.main import main
from tests.fakes.apps.app_server import AppServer


class TestSwarmMissionsMain:
    SCRIPT: ClassVar[str] = "swarm-missions-serve"
    TARGET: ClassVar[str] = "swarm_missions.main:main"
    APP_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[2] / "backend" / "apps" / "missions"
    INFO_KEY: ClassVar[str] = "info"
    TITLE_KEY: ClassVar[str] = "title"

    def test_the_console_script_points_to_main(self) -> None:
        assert entry_points(group="console_scripts")[self.SCRIPT].value == self.TARGET

    def test_main_takes_no_argument(self) -> None:
        assert not signature(main).parameters

    def test_the_app_serves_its_api_from_the_folder_the_entry_names(self, tmp_path: Path) -> None:
        with AppServer(self.SCRIPT, self.APP_FOLDER, tmp_path) as server:
            response = server.get_openapi()

        assert response.status_code == httpx.codes.OK
        assert response.json()[self.INFO_KEY][self.TITLE_KEY] == MissionsRouter.TITLE
