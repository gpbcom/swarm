from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from gateway.models.live.exceptions import (
    SEInvalidLiveConfigException,
    SELiveConfigInvalidNats,
    SELiveConfigInvalidSession,
    SELiveConfigInvalidStatusInterval,
)
from gateway.models.live.live_config import LiveConfig
from swarm_nats.models.config.exceptions import SENatsClientConfigInvalidName
from swarm_nats.models.config.nats_client_config import NatsClientConfig

from swarm_live.models.config.live_session_config import LiveSessionConfig  # isort: skip


class TestGatewayLiveConfig:
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SELiveConfigInvalidStatusInterval,
        SELiveConfigInvalidNats,
        SELiveConfigInvalidSession,
    ]
    FULL: ClassVar[Dict[str, JsonValue]] = {
        "status_interval_s": 2.5,
        "nats": {"servers": ["nats://127.0.0.1:4333"]},
        "session": {"status_interval_s": 1.5},
    }
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    BAD_NAME_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"nats": {"name": ""}}

    def test_defaults(self) -> None:
        config = LiveConfig()
        assert config.status_interval_s == 5.0
        assert config.nats == NatsClientConfig()
        assert config.session == LiveSessionConfig()

    def test_full_valid_construction(self) -> None:
        config = LiveConfig.model_validate(self.FULL)
        assert config.status_interval_s == 2.5
        assert config.nats == NatsClientConfig(servers=["nats://127.0.0.1:4333"])
        assert config.session == LiveSessionConfig(status_interval_s=1.5)

    @pytest.mark.parametrize("name", ["status_interval_s", "nats", "session"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = LiveConfig.model_validate({name: None})
        default = LiveConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("status_interval_s", 0, SELiveConfigInvalidStatusInterval),
            ("status_interval_s", -1.0, SELiveConfigInvalidStatusInterval),
            ("status_interval_s", "5", SELiveConfigInvalidStatusInterval),
            ("status_interval_s", True, SELiveConfigInvalidStatusInterval),
            ("nats", "nats://127.0.0.1:4222", SELiveConfigInvalidNats),
            ("nats", 3, SELiveConfigInvalidNats),
            ("nats", [1], SELiveConfigInvalidNats),
            ("session", 5.0, SELiveConfigInvalidSession),
            ("session", "full", SELiveConfigInvalidSession),
            ("session", [1], SELiveConfigInvalidSession),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            LiveConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            LiveConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = LiveConfig.model_validate(self.FULL)
        assert LiveConfig.model_validate(config.model_dump()) == config

    def test_a_nested_nats_error_is_raised_unchanged(self) -> None:
        with pytest.raises(SENatsClientConfigInvalidName):
            LiveConfig.model_validate(self.BAD_NAME_CONFIGURATION)

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidLiveConfigException)
