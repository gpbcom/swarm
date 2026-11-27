from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.config.gateway.exceptions import (
    SEInvalidOperatorDirectoryConfigException,
    SEOperatorDirectoryConfigInvalidCell,
    SEOperatorDirectoryConfigInvalidKeycloak,
)
from swarm_models.config.gateway.operator_directory_config import OperatorDirectoryConfig
from swarm_models.keycloak.exceptions import SEKeycloakAdminConfigInvalidRealm
from swarm_models.keycloak.keycloak_admin_config import KeycloakAdminConfig


class TestOperatorDirectoryConfig:
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEOperatorDirectoryConfigInvalidCell,
        SEOperatorDirectoryConfigInvalidKeycloak,
    ]
    FULL: ClassVar[Dict[str, JsonValue]] = {"cell": "eu_west", "keycloak": {"realm": "other"}}
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    BAD_REALM_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"keycloak": {"realm": ""}}

    def test_defaults(self) -> None:
        config = OperatorDirectoryConfig()
        assert config.cell == "dev"
        assert config.keycloak == KeycloakAdminConfig()

    def test_full_valid_construction(self) -> None:
        config = OperatorDirectoryConfig.model_validate(self.FULL)
        assert config.cell == "eu_west"
        assert config.keycloak == KeycloakAdminConfig(realm="other")

    @pytest.mark.parametrize("name", ["cell", "keycloak"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = OperatorDirectoryConfig.model_validate({name: None})
        default = OperatorDirectoryConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("cell", "", SEOperatorDirectoryConfigInvalidCell),
            ("cell", "   ", SEOperatorDirectoryConfigInvalidCell),
            ("cell", 3, SEOperatorDirectoryConfigInvalidCell),
            ("cell", True, SEOperatorDirectoryConfigInvalidCell),
            ("cell", "Dev", SEOperatorDirectoryConfigInvalidCell),
            ("keycloak", "http://keycloak", SEOperatorDirectoryConfigInvalidKeycloak),
            ("keycloak", 3, SEOperatorDirectoryConfigInvalidKeycloak),
            ("keycloak", [1], SEOperatorDirectoryConfigInvalidKeycloak),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            OperatorDirectoryConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            OperatorDirectoryConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = OperatorDirectoryConfig.model_validate(self.FULL)
        assert OperatorDirectoryConfig.model_validate(config.model_dump()) == config

    def test_a_nested_keycloak_error_is_raised_unchanged(self) -> None:
        with pytest.raises(SEKeycloakAdminConfigInvalidRealm):
            OperatorDirectoryConfig.model_validate(self.BAD_REALM_CONFIGURATION)

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidOperatorDirectoryConfigException)
