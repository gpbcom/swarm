from __future__ import annotations

import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Iterator, Optional

import pytest
import yaml

from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.formatters.coloured_formatter import ColouredFormatter
from swarm_logging.formatters.json_formatter import JsonFormatter
from swarm_logging.models.enums import LogFormat
from swarm_logging.models.exceptions import (
    SELoggingConfigurationRefusedError,
    SELoggingConfigurationUnreadableError,
    SELoggingError,
)
from swarm_logging.models.logging_config import LoggingConfig


class TestLoggingConfigurator:
    @pytest.fixture(autouse=True)
    def restore_root_logger(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
        monkeypatch.chdir(tmp_path)
        root = logging.getLogger()
        saved_handlers = list(root.handlers)
        saved_level = root.level
        yield
        for handler in list(root.handlers):
            if handler not in saved_handlers:
                handler.close()
                root.removeHandler(handler)
        root.setLevel(saved_level)

    def write_config(self, tmp_path: Path, content: str) -> Path:
        path = tmp_path / "custom.yaml"
        path.write_text(content, encoding="utf-8")
        return path

    def flush_root(self) -> None:
        for handler in logging.getLogger().handlers:
            handler.flush()

    def test_the_reference_file_exists_and_holds_the_reference_configuration(self) -> None:
        assert LoggingConfigurator.REFERENCE_PATH.is_file()
        content = yaml.safe_load(LoggingConfigurator.REFERENCE_PATH.read_text(encoding="utf-8"))
        assert content["version"] == 1
        assert content["disable_existing_loggers"] is False
        coloured = content["formatters"]["coloured"]
        assert coloured["()"] == "swarm_logging.formatters.coloured_formatter.ColouredFormatter"
        assert coloured["format"]
        console = content["handlers"]["console"]
        assert console["class"] == "logging.StreamHandler"
        assert console["stream"] == "ext://sys.stderr"
        assert console["formatter"] == "coloured"
        file_handler = content["handlers"]["file"]
        assert file_handler["class"] == "logging.handlers.RotatingFileHandler"
        assert file_handler["filename"] == "logs/swarm.log"
        assert "maxBytes" in file_handler
        assert "backupCount" in file_handler
        assert file_handler["encoding"] == "utf-8"
        assert file_handler["formatter"] == "coloured"
        assert content["root"]["level"] == "DEBUG"
        assert set(content["root"]["handlers"]) == {"console", "file"}

    def test_the_default_configuration_sets_the_root_level_to_debug(self) -> None:
        LoggingConfigurator(LoggingConfig()).configure()
        assert logging.getLogger().level == logging.DEBUG

    def test_the_default_configuration_adds_a_coloured_console_and_a_coloured_rotating_file(self) -> None:
        LoggingConfigurator(LoggingConfig()).configure()
        handlers = logging.getLogger().handlers
        streams = [h for h in handlers if type(h) is logging.StreamHandler]
        files = [h for h in handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
        assert len(streams) == 1
        assert len(files) == 1
        assert isinstance(streams[0].formatter, ColouredFormatter)
        assert isinstance(files[0].formatter, ColouredFormatter)

    def test_the_default_configuration_creates_the_log_file_with_colour_codes(self, tmp_path: Path) -> None:
        LoggingConfigurator(LoggingConfig()).configure()
        logging.getLogger("tests.logging_configurator").info("a coloured line")
        self.flush_root()
        log_file = tmp_path / "logs" / "swarm.log"
        assert log_file.is_file()
        assert "\x1b[" in log_file.read_text(encoding="utf-8")

    def test_the_json_format_replaces_every_formatter(self) -> None:
        LoggingConfigurator(LoggingConfig(format="json")).configure()
        handlers = logging.getLogger().handlers
        assert handlers
        for handler in handlers:
            assert isinstance(handler.formatter, JsonFormatter)

    def test_the_json_format_writes_one_json_document_per_line(self, tmp_path: Path) -> None:
        LoggingConfigurator(LoggingConfig(format=LogFormat.JSON)).configure()
        logging.getLogger("tests.logging_configurator").info("a json line")
        self.flush_root()
        lines = (tmp_path / "logs" / "swarm.log").read_text(encoding="utf-8").strip().splitlines()
        document = json.loads(lines[-1])
        assert "a json line" in [str(value) for value in document.values()]

    def test_a_custom_path_creates_its_folder_and_is_used(self, tmp_path: Path) -> None:
        configuration: Dict[str, object] = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {"file": {"class": "logging.FileHandler", "filename": "out/custom.log", "encoding": "utf-8"}},
            "root": {"level": "INFO", "handlers": ["file"]},
        }
        path = self.write_config(tmp_path, yaml.safe_dump(configuration))
        LoggingConfigurator(LoggingConfig(path=path)).configure()
        logging.getLogger("tests.logging_configurator").info("a custom line")
        self.flush_root()
        assert (tmp_path / "out").is_dir()
        assert "a custom line" in (tmp_path / "out" / "custom.log").read_text(encoding="utf-8")
        assert not (tmp_path / "logs").exists()

    @pytest.mark.parametrize(
        "content",
        [None, "key: [unclosed", "- one\n- two\n"],
        ids=["missing file", "invalid yaml", "yaml list"],
    )
    def test_an_unreadable_configuration_is_refused(self, tmp_path: Path, content: Optional[str]) -> None:
        path = tmp_path / "missing.yaml" if content is None else self.write_config(tmp_path, content)
        with pytest.raises(SELoggingConfigurationUnreadableError) as raised:
            LoggingConfigurator(LoggingConfig(path=path)).configure()
        assert isinstance(raised.value, SELoggingError)

    def test_a_handler_with_an_unknown_class_is_refused_with_its_cause(self, tmp_path: Path) -> None:
        configuration: Dict[str, object] = {
            "version": 1,
            "handlers": {"bad": {"class": "no.such.module.Handler"}},
            "root": {"level": "INFO", "handlers": ["bad"]},
        }
        path = self.write_config(tmp_path, yaml.safe_dump(configuration))
        with pytest.raises(SELoggingConfigurationRefusedError) as raised:
            LoggingConfigurator(LoggingConfig(path=path)).configure()
        assert isinstance(raised.value, SELoggingError)
        assert raised.value.__cause__ is not None
