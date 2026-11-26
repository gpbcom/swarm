from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.auth.auth_config import AuthConfig
from swarm_models.auth.exceptions import (
    SEAuthConfigInvalidAudience,
    SEAuthConfigInvalidIssuerUrl,
    SEAuthConfigInvalidJwksCacheTtlS,
    SEAuthConfigInvalidLeewayS,
    SEAuthConfigInvalidRequestTimeoutS,
    SEInvalidAuthConfigException,
)


class TestAuthConfig:
    ISSUER: ClassVar[str] = "https://id.example.org/realms/swarm"
    REQUIRED: ClassVar[Dict[str, JsonValue]] = {"issuer_url": ISSUER}
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEAuthConfigInvalidIssuerUrl,
        SEAuthConfigInvalidAudience,
        SEAuthConfigInvalidJwksCacheTtlS,
        SEAuthConfigInvalidLeewayS,
        SEAuthConfigInvalidRequestTimeoutS,
    ]
    FULL: ClassVar[Dict[str, JsonValue]] = {
        "issuer_url": "http://localhost:8080/realms/other",
        "audience": "other-audience",
        "jwks_cache_ttl_s": 60.5,
        "leeway_s": 2.5,
        "request_timeout_s": 1.5,
    }
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"issuer_url": ISSUER, "colour": "red"}

    def test_defaults(self) -> None:
        config = AuthConfig.model_validate(self.REQUIRED)
        assert config.issuer_url == self.ISSUER
        assert config.audience == "swarm-gateway"
        assert config.jwks_cache_ttl_s == 300.0
        assert config.leeway_s == 0.0
        assert config.request_timeout_s == 5.0

    def test_full_valid_construction(self) -> None:
        config = AuthConfig.model_validate(self.FULL)
        assert config.issuer_url == self.FULL["issuer_url"]
        assert config.audience == self.FULL["audience"]
        assert config.jwks_cache_ttl_s == self.FULL["jwks_cache_ttl_s"]
        assert config.leeway_s == self.FULL["leeway_s"]
        assert config.request_timeout_s == self.FULL["request_timeout_s"]

    @pytest.mark.parametrize("name", ["audience", "jwks_cache_ttl_s", "leeway_s", "request_timeout_s"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = AuthConfig.model_validate({**self.REQUIRED, name: None})
        default = AuthConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    def test_the_issuer_url_has_no_default(self) -> None:
        assert AuthConfig.model_fields["issuer_url"].is_required()

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("issuer_url", None, SEAuthConfigInvalidIssuerUrl),
            ("issuer_url", "", SEAuthConfigInvalidIssuerUrl),
            ("issuer_url", "   ", SEAuthConfigInvalidIssuerUrl),
            ("issuer_url", 3, SEAuthConfigInvalidIssuerUrl),
            ("issuer_url", True, SEAuthConfigInvalidIssuerUrl),
            ("issuer_url", "ftp://id.example.org", SEAuthConfigInvalidIssuerUrl),
            ("issuer_url", "id.example.org/realms/swarm", SEAuthConfigInvalidIssuerUrl),
            ("audience", "", SEAuthConfigInvalidAudience),
            ("audience", "   ", SEAuthConfigInvalidAudience),
            ("audience", 3, SEAuthConfigInvalidAudience),
            ("audience", True, SEAuthConfigInvalidAudience),
            ("jwks_cache_ttl_s", 0, SEAuthConfigInvalidJwksCacheTtlS),
            ("jwks_cache_ttl_s", -1.0, SEAuthConfigInvalidJwksCacheTtlS),
            ("jwks_cache_ttl_s", "300", SEAuthConfigInvalidJwksCacheTtlS),
            ("jwks_cache_ttl_s", True, SEAuthConfigInvalidJwksCacheTtlS),
            ("leeway_s", -0.5, SEAuthConfigInvalidLeewayS),
            ("leeway_s", "1", SEAuthConfigInvalidLeewayS),
            ("leeway_s", False, SEAuthConfigInvalidLeewayS),
            ("request_timeout_s", 0, SEAuthConfigInvalidRequestTimeoutS),
            ("request_timeout_s", -5, SEAuthConfigInvalidRequestTimeoutS),
            ("request_timeout_s", "5", SEAuthConfigInvalidRequestTimeoutS),
            ("request_timeout_s", True, SEAuthConfigInvalidRequestTimeoutS),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            AuthConfig.model_validate({**self.REQUIRED, name: value})

    def test_a_missing_issuer_url_is_refused(self) -> None:
        with pytest.raises((ValidationError, SEAuthConfigInvalidIssuerUrl)):
            AuthConfig.model_validate({})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            AuthConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = AuthConfig.model_validate(self.FULL)
        assert AuthConfig.model_validate(config.model_dump()) == config

    def test_the_model_is_frozen(self) -> None:
        config = AuthConfig.model_validate(self.REQUIRED)
        with pytest.raises(ValidationError):
            config.audience = "other"

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("  https://id.example.org/realms/swarm  ", "https://id.example.org/realms/swarm"),
            ("https://id.example.org/realms/swarm/", "https://id.example.org/realms/swarm"),
            ("http://localhost:8080/", "http://localhost:8080"),
        ],
    )
    def test_the_issuer_url_is_stripped_and_loses_its_trailing_slash(self, value: str, expected: str) -> None:
        assert AuthConfig.model_validate({"issuer_url": value}).issuer_url == expected

    def test_the_audience_is_stripped(self) -> None:
        config = AuthConfig.model_validate({**self.REQUIRED, "audience": "  swarm-api  "})
        assert config.audience == "swarm-api"

    def test_a_zero_leeway_is_accepted(self) -> None:
        assert AuthConfig.model_validate({**self.REQUIRED, "leeway_s": 0}).leeway_s == 0

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidAuthConfigException)
