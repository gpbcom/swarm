from __future__ import annotations

from typing import ClassVar, Dict, List

import pytest
from pydantic import JsonValue, ValidationError

from swarm_nats.models.config.exceptions import (
    SEInvalidNatsClientConfigException,
    SENatsClientConfigInvalidConnectTimeout,
    SENatsClientConfigInvalidCredentialsPath,
    SENatsClientConfigInvalidName,
    SENatsClientConfigInvalidReconnectWait,
    SENatsClientConfigInvalidRequestDeadline,
    SENatsClientConfigInvalidServers,
)
from swarm_nats.models.config.nats_client_config import NatsClientConfig


class TestNatsClientConfig:
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    DEFAULT_SERVERS: ClassVar[List[str]] = ["nats://127.0.0.1:4222"]
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SENatsClientConfigInvalidServers,
        SENatsClientConfigInvalidName,
        SENatsClientConfigInvalidCredentialsPath,
        SENatsClientConfigInvalidConnectTimeout,
        SENatsClientConfigInvalidReconnectWait,
        SENatsClientConfigInvalidRequestDeadline,
    ]

    def test_defaults(self) -> None:
        config = NatsClientConfig()
        assert config.servers == self.DEFAULT_SERVERS
        assert config.name == "swarm"
        assert config.credentials_path is None
        assert config.connect_timeout_s == 2.0
        assert config.reconnect_wait_s == 2.0
        assert config.request_deadline_s == 5.0

    def test_full_valid_construction(self) -> None:
        config = NatsClientConfig(
            servers=["nats://a:4222", "tls://b:4223"],
            name="gateway",
            credentials_path="/run/secrets/gateway.creds",
            connect_timeout_s=1.5,
            reconnect_wait_s=0.5,
            request_deadline_s=10.0,
        )
        assert config.servers == ["nats://a:4222", "tls://b:4223"]
        assert config.name == "gateway"
        assert config.credentials_path == "/run/secrets/gateway.creds"
        assert config.connect_timeout_s == 1.5
        assert config.reconnect_wait_s == 0.5
        assert config.request_deadline_s == 10.0

    @pytest.mark.parametrize(
        "name",
        ["servers", "name", "credentials_path", "connect_timeout_s", "reconnect_wait_s", "request_deadline_s"],
    )
    def test_none_becomes_the_default(self, name: str) -> None:
        config = NatsClientConfig.model_validate({name: None})
        default = NatsClientConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("servers", [], SENatsClientConfigInvalidServers),
            ("servers", "nats://a:4222", SENatsClientConfigInvalidServers),
            ("servers", 3, SENatsClientConfigInvalidServers),
            ("servers", [3], SENatsClientConfigInvalidServers),
            ("servers", [""], SENatsClientConfigInvalidServers),
            ("servers", ["http://a:4222"], SENatsClientConfigInvalidServers),
            ("servers", ["a:4222"], SENatsClientConfigInvalidServers),
            ("servers", ["nats://"], SENatsClientConfigInvalidServers),
            ("servers", ["nats://a b:4222"], SENatsClientConfigInvalidServers),
            ("servers", ["nats://a:4222/path"], SENatsClientConfigInvalidServers),
            ("servers", ["nats://a:4222", "ws://b"], SENatsClientConfigInvalidServers),
            ("name", "", SENatsClientConfigInvalidName),
            ("name", "   ", SENatsClientConfigInvalidName),
            ("name", 3, SENatsClientConfigInvalidName),
            ("credentials_path", "", SENatsClientConfigInvalidCredentialsPath),
            ("credentials_path", "   ", SENatsClientConfigInvalidCredentialsPath),
            ("credentials_path", 3, SENatsClientConfigInvalidCredentialsPath),
            ("connect_timeout_s", 0, SENatsClientConfigInvalidConnectTimeout),
            ("connect_timeout_s", -1.0, SENatsClientConfigInvalidConnectTimeout),
            ("connect_timeout_s", True, SENatsClientConfigInvalidConnectTimeout),
            ("connect_timeout_s", "2", SENatsClientConfigInvalidConnectTimeout),
            ("reconnect_wait_s", 0, SENatsClientConfigInvalidReconnectWait),
            ("reconnect_wait_s", -1.0, SENatsClientConfigInvalidReconnectWait),
            ("reconnect_wait_s", True, SENatsClientConfigInvalidReconnectWait),
            ("reconnect_wait_s", "2", SENatsClientConfigInvalidReconnectWait),
            ("request_deadline_s", 0, SENatsClientConfigInvalidRequestDeadline),
            ("request_deadline_s", -1.0, SENatsClientConfigInvalidRequestDeadline),
            ("request_deadline_s", True, SENatsClientConfigInvalidRequestDeadline),
            ("request_deadline_s", "5", SENatsClientConfigInvalidRequestDeadline),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            NatsClientConfig.model_validate({name: value})

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidNatsClientConfigException)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            NatsClientConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_a_name_with_surrounding_spaces_is_stripped(self) -> None:
        assert NatsClientConfig(name="  gateway  ").name == "gateway"

    def test_a_credentials_path_with_surrounding_spaces_is_stripped(self) -> None:
        assert NatsClientConfig(credentials_path="  /a.creds  ").credentials_path == "/a.creds"

    def test_round_trip(self) -> None:
        config = NatsClientConfig(servers=["tls://a:4222"], name="gateway", credentials_path="/a.creds")
        data: Dict[str, JsonValue] = config.model_dump()
        assert NatsClientConfig.model_validate(data) == config
