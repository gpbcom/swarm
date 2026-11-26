from __future__ import annotations

# Standard library imports
from importlib.metadata import entry_points
from typing import ClassVar

# Third-party imports
import pytest

pytest.importorskip("swarm_core")

# First-party imports
from flight_engine.api.cli.main import main  # isort: skip


class TestFlightEngineMain:
    SCRIPT_NAME: ClassVar[str] = "swarm-flight-engine"
    TARGET: ClassVar[str] = "flight_engine.api.cli.main:main"

    def test_the_console_script_points_at_main(self) -> None:
        scripts = {entry.name: entry.value for entry in entry_points(group="console_scripts")}

        assert scripts.get(self.SCRIPT_NAME) == self.TARGET

    def test_main_is_callable(self) -> None:
        assert callable(main)
