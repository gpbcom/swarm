from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, Optional

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_logging.models.enums import LogFormat
from swarm_logging.models.exceptions import (
    SEInvalidLoggingConfigException,
    SELoggingConfigInvalidFormat,
    SELoggingConfigInvalidPath,
)
from swarm_logging.models.logging_config import LoggingConfig


class TestLoggingConfig:
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    JSON_FORMAT_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"format": "json"}

    def test_defaults(self) -> None:
        config = LoggingConfig()
        assert config.path is None
        assert config.format is LogFormat.COLOURED

    def test_full_valid_construction(self) -> None:
        config = LoggingConfig(path="conf/logger.yaml", format=LogFormat.JSON)
        assert config.path == "conf/logger.yaml"
        assert config.format is LogFormat.JSON

    @pytest.mark.parametrize(("name", "default"), [("path", None), ("format", LogFormat.COLOURED)])
    def test_none_becomes_the_default(self, name: str, default: Optional[LogFormat]) -> None:
        config = LoggingConfig.model_validate({name: None})
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("path", "", SELoggingConfigInvalidPath),
            ("path", "   ", SELoggingConfigInvalidPath),
            ("path", 3, SELoggingConfigInvalidPath),
            ("format", "xml", SELoggingConfigInvalidFormat),
            ("format", True, SELoggingConfigInvalidFormat),
            ("format", 3, SELoggingConfigInvalidFormat),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            LoggingConfig.model_validate({name: value})

    @pytest.mark.parametrize("error", [SELoggingConfigInvalidPath, SELoggingConfigInvalidFormat])
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidLoggingConfigException)
        assert not issubclass(error, ValueError)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            LoggingConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_a_path_with_surrounding_spaces_is_stripped(self) -> None:
        assert LoggingConfig(path="  conf/logger.yaml  ").path == "conf/logger.yaml"

    def test_the_json_string_gives_the_json_format(self) -> None:
        assert LoggingConfig.model_validate(self.JSON_FORMAT_CONFIGURATION).format is LogFormat.JSON

    def test_round_trip(self) -> None:
        config = LoggingConfig(path="conf/logger.yaml", format=LogFormat.JSON)
        data: Dict[str, JsonValue] = config.model_dump()
        assert LoggingConfig.model_validate(data) == config
