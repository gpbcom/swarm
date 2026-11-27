from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.keycloak.exceptions import (
    SEInvalidKeycloakAdminConfigException,
    SEKeycloakAdminConfigInvalidClientId,
    SEKeycloakAdminConfigInvalidClientSecretKey,
    SEKeycloakAdminConfigInvalidRealm,
    SEKeycloakAdminConfigInvalidRequestTimeoutS,
    SEKeycloakAdminConfigInvalidServerUrl,
    SEKeycloakAdminConfigInvalidSignInClientId,
)
from swarm_models.keycloak.keycloak_admin_config import KeycloakAdminConfig


class TestKeycloakAdminConfig:
    FIELDS: ClassVar[List[str]] = [
        "server_url",
        "realm",
        "client_id",
        "client_secret_key",
        "sign_in_client_id",
        "request_timeout_s",
    ]
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEKeycloakAdminConfigInvalidServerUrl,
        SEKeycloakAdminConfigInvalidRealm,
        SEKeycloakAdminConfigInvalidClientId,
        SEKeycloakAdminConfigInvalidClientSecretKey,
        SEKeycloakAdminConfigInvalidSignInClientId,
        SEKeycloakAdminConfigInvalidRequestTimeoutS,
    ]
    FULL: ClassVar[Dict[str, JsonValue]] = {
        "server_url": "https://id.example.org",
        "realm": "other",
        "client_id": "other-admin",
        "client_secret_key": "SWARM_OTHER_SECRET",
        "sign_in_client_id": "client-portal",
        "request_timeout_s": 1.5,
    }
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}

    def test_defaults(self) -> None:
        config = KeycloakAdminConfig()
        assert config.server_url == "http://keycloak.global.svc.cluster.local:8080"
        assert config.realm == "swarm"
        assert config.client_id == "swarm-gateway-admin"
        assert config.client_secret_key == "SWARM_GATEWAY_KEYCLOAK_CLIENT_SECRET"
        assert config.sign_in_client_id == "back-office"
        assert config.request_timeout_s == 5.0

    def test_full_valid_construction(self) -> None:
        config = KeycloakAdminConfig.model_validate(self.FULL)
        for name, value in self.FULL.items():
            assert getattr(config, name) == value

    @pytest.mark.parametrize("name", FIELDS)
    def test_none_becomes_the_default(self, name: str) -> None:
        config = KeycloakAdminConfig.model_validate({name: None})
        default = KeycloakAdminConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("server_url", "", SEKeycloakAdminConfigInvalidServerUrl),
            ("server_url", "   ", SEKeycloakAdminConfigInvalidServerUrl),
            ("server_url", 3, SEKeycloakAdminConfigInvalidServerUrl),
            ("server_url", True, SEKeycloakAdminConfigInvalidServerUrl),
            ("server_url", "keycloak:8080", SEKeycloakAdminConfigInvalidServerUrl),
            ("realm", "", SEKeycloakAdminConfigInvalidRealm),
            ("realm", "  ", SEKeycloakAdminConfigInvalidRealm),
            ("realm", 3, SEKeycloakAdminConfigInvalidRealm),
            ("realm", True, SEKeycloakAdminConfigInvalidRealm),
            ("client_id", "", SEKeycloakAdminConfigInvalidClientId),
            ("client_id", "  ", SEKeycloakAdminConfigInvalidClientId),
            ("client_id", 3, SEKeycloakAdminConfigInvalidClientId),
            ("client_id", True, SEKeycloakAdminConfigInvalidClientId),
            ("client_secret_key", "", SEKeycloakAdminConfigInvalidClientSecretKey),
            ("client_secret_key", "  ", SEKeycloakAdminConfigInvalidClientSecretKey),
            ("client_secret_key", 3, SEKeycloakAdminConfigInvalidClientSecretKey),
            ("client_secret_key", True, SEKeycloakAdminConfigInvalidClientSecretKey),
            ("sign_in_client_id", "", SEKeycloakAdminConfigInvalidSignInClientId),
            ("sign_in_client_id", "  ", SEKeycloakAdminConfigInvalidSignInClientId),
            ("sign_in_client_id", 3, SEKeycloakAdminConfigInvalidSignInClientId),
            ("sign_in_client_id", True, SEKeycloakAdminConfigInvalidSignInClientId),
            ("request_timeout_s", 0, SEKeycloakAdminConfigInvalidRequestTimeoutS),
            ("request_timeout_s", -1.0, SEKeycloakAdminConfigInvalidRequestTimeoutS),
            ("request_timeout_s", True, SEKeycloakAdminConfigInvalidRequestTimeoutS),
            ("request_timeout_s", "5", SEKeycloakAdminConfigInvalidRequestTimeoutS),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            KeycloakAdminConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            KeycloakAdminConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = KeycloakAdminConfig.model_validate(self.FULL)
        assert KeycloakAdminConfig.model_validate(config.model_dump()) == config

    def test_a_trailing_slash_of_the_server_url_is_not_kept(self) -> None:
        config = KeycloakAdminConfig.model_validate({"server_url": "https://id.example.org/"})
        assert config.server_url == "https://id.example.org"

    def test_an_integer_timeout_is_accepted(self) -> None:
        assert KeycloakAdminConfig.model_validate({"request_timeout_s": 3}).request_timeout_s == 3

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidKeycloakAdminConfigException)
