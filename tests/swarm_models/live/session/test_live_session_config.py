from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.live.session.exceptions import SELiveSessionConfigInvalidStatusInterval  # isort: skip
from swarm_models.live.session.live_session_config import LiveSessionConfig  # isort: skip


class TestLiveSessionConfig:
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}

    def test_defaults(self) -> None:
        assert LiveSessionConfig().status_interval_s == 5.0

    def test_full_valid_construction(self) -> None:
        assert LiveSessionConfig(status_interval_s=2.5).status_interval_s == 2.5

    def test_none_becomes_the_default(self) -> None:
        config = LiveSessionConfig.model_validate({"status_interval_s": None})
        default = LiveSessionConfig.model_fields["status_interval_s"].get_default(call_default_factory=True)
        assert config.status_interval_s == default

    @pytest.mark.parametrize("value", [0, -1.0, True, "5"])
    def test_rejects_bad_values(self, value: JsonValue) -> None:
        with pytest.raises(SELiveSessionConfigInvalidStatusInterval):
            LiveSessionConfig.model_validate({"status_interval_s": value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            LiveSessionConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = LiveSessionConfig(status_interval_s=1.5)
        data: Dict[str, JsonValue] = config.model_dump()
        assert LiveSessionConfig.model_validate(data) == config
