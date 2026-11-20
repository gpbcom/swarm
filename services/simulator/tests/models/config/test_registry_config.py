from __future__ import annotations

from typing import ClassVar, Dict, List

import pytest
from pydantic import JsonValue, ValidationError

from simulator.models.config.exceptions import (
    SERegistryConfigInvalidCommandMappingPath,
    SERegistryConfigInvalidSimulatedHosts,
    SERegistryConfigInvalidSquadCatalogPath,
)
from simulator.models.config.registry_config import RegistryConfig


class TestRegistryConfig:
    DEFAULT_HOSTS: ClassVar[List[str]] = ["synthetic-drones", "px4-sitl", "127.0.0.1", "localhost"]
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"simulated_hosts": ["a"], "colour": "red"}

    def test_defaults(self) -> None:
        config = RegistryConfig()
        assert config.squad_catalog_path == "conf/catalogs/simulated_squad.yaml"
        assert config.command_mapping_path == "conf/catalogs/command_mapping.yaml"
        assert config.simulated_hosts == self.DEFAULT_HOSTS

    def test_full_valid_construction(self) -> None:
        config = RegistryConfig(
            squad_catalog_path="a/squad.yaml",
            command_mapping_path="a/mapping.yaml",
            simulated_hosts=["sim-1", "sim-2"],
        )
        assert config.squad_catalog_path == "a/squad.yaml"
        assert config.command_mapping_path == "a/mapping.yaml"
        assert config.simulated_hosts == ["sim-1", "sim-2"]

    @pytest.mark.parametrize("name", ["squad_catalog_path", "command_mapping_path", "simulated_hosts"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = RegistryConfig.model_validate({name: None})
        default = RegistryConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("squad_catalog_path", "", SERegistryConfigInvalidSquadCatalogPath),
            ("squad_catalog_path", "   ", SERegistryConfigInvalidSquadCatalogPath),
            ("squad_catalog_path", 3, SERegistryConfigInvalidSquadCatalogPath),
            ("command_mapping_path", "", SERegistryConfigInvalidCommandMappingPath),
            ("command_mapping_path", "   ", SERegistryConfigInvalidCommandMappingPath),
            ("command_mapping_path", 3, SERegistryConfigInvalidCommandMappingPath),
            ("simulated_hosts", [], SERegistryConfigInvalidSimulatedHosts),
            ("simulated_hosts", ["a", "a"], SERegistryConfigInvalidSimulatedHosts),
            ("simulated_hosts", "localhost", SERegistryConfigInvalidSimulatedHosts),
            ("simulated_hosts", [3], SERegistryConfigInvalidSimulatedHosts),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            RegistryConfig.model_validate({name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            RegistryConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    @pytest.mark.parametrize("name", ["squad_catalog_path", "command_mapping_path"])
    def test_a_path_with_surrounding_spaces_is_stripped(self, name: str) -> None:
        assert getattr(RegistryConfig.model_validate({name: "  a/b.yaml  "}), name) == "a/b.yaml"

    def test_the_default_hosts_are_not_shared_between_instances(self) -> None:
        first = RegistryConfig()
        first.simulated_hosts.append("extra")
        assert RegistryConfig().simulated_hosts == self.DEFAULT_HOSTS

    def test_round_trip(self) -> None:
        config = RegistryConfig(squad_catalog_path="x.yaml", simulated_hosts=["h1", "h2"])
        data: Dict[str, JsonValue] = config.model_dump()
        assert RegistryConfig.model_validate(data) == config
