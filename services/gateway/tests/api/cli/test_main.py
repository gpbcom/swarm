from __future__ import annotations

# Standard library imports
import logging
import logging.handlers
from importlib.metadata import entry_points
from pathlib import Path
from typing import Iterator

# Third-party imports
import pytest

# First-party imports
from gateway.api.cli.main import main


class TestMain:
    @pytest.fixture(autouse=True)
    def restore_root_logger(self) -> Iterator[None]:
        root = logging.getLogger()
        handlers = list(root.handlers)
        level = root.level
        yield
        for handler in list(root.handlers):
            if handler not in handlers:
                handler.close()
                root.removeHandler(handler)
        root.setLevel(level)

    def test_main_prints_the_greeting_and_returns(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.chdir(tmp_path)

        main()

        assert capsys.readouterr().out == "Hello from swarm!\n"

    def test_main_writes_the_log_file_under_the_current_folder(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.chdir(tmp_path)

        main()

        assert (tmp_path / "logs" / "swarm.log").exists()

    def test_main_gives_the_root_logger_a_rotating_file_handler(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.chdir(tmp_path)

        main()

        kinds = [type(handler) for handler in logging.getLogger().handlers]
        assert logging.handlers.RotatingFileHandler in kinds

    def test_the_console_script_points_at_main(self) -> None:
        scripts = {entry.name: entry.value for entry in entry_points(group="console_scripts")}

        assert scripts.get("swarm-gateway") == "gateway.api.cli.main:main"
