from __future__ import annotations

from importlib.metadata import entry_points

import pytest
from gateway.api.cli.main import main


class TestMain:
    def test_main_prints_the_greeting(self, capsys: pytest.CaptureFixture[str]) -> None:
        main()

        assert capsys.readouterr().out == "Hello from swarm!\n"

    def test_the_console_script_points_at_main(self) -> None:
        scripts = {entry.name: entry.value for entry in entry_points(group="console_scripts")}

        assert scripts.get("swarm-gateway") == "gateway.api.cli.main:main"
