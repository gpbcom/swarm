from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator

# First-party imports
from simulator.models.config.exceptions import (
    SERegistryConfigInvalidCommandMappingPath,
    SERegistryConfigInvalidSimulatedHosts,
    SERegistryConfigInvalidSquadCatalogPath,
)


class RegistryConfig(BaseModel):
    """Where the simulated squad and the command mapping are read, and which hosts are simulated.

    Attributes:
        squad_catalog_path (str): The path of the catalogue of the simulated squad.
        command_mapping_path (str): The path of the catalogue that maps commands to MAVLink.
        simulated_hosts (List[str]): The hosts a drone may be reached at to count as simulated.
        SQUAD_CATALOG_PATH_FIELD (str): The name of the ``squad_catalog_path`` field.
        COMMAND_MAPPING_PATH_FIELD (str): The name of the ``command_mapping_path`` field.
        SIMULATED_HOSTS_FIELD (str): The name of the ``simulated_hosts`` field.
        DEFAULT_SQUAD_CATALOG_PATH (str): The default path of the squad catalogue.
        DEFAULT_COMMAND_MAPPING_PATH (str): The default path of the command mapping.
        DEFAULT_SIMULATED_HOSTS (List[str]): The default simulated hosts.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.

    Notes:
        - The simulated hosts are what keeps a simulated command from reaching a real drone.
    """

    SQUAD_CATALOG_PATH_FIELD: ClassVar[str] = "squad_catalog_path"
    COMMAND_MAPPING_PATH_FIELD: ClassVar[str] = "command_mapping_path"
    SIMULATED_HOSTS_FIELD: ClassVar[str] = "simulated_hosts"
    DEFAULT_SQUAD_CATALOG_PATH: ClassVar[str] = "conf/catalogs/simulated_squad.yaml"
    DEFAULT_COMMAND_MAPPING_PATH: ClassVar[str] = "conf/catalogs/command_mapping.yaml"
    DEFAULT_SIMULATED_HOSTS: ClassVar[List[str]] = ["synthetic-drones", "px4-sitl", "127.0.0.1", "localhost"]
    BEFORE: ClassVar[Literal["before"]] = "before"

    model_config = ConfigDict(extra="forbid", validate_default=True)

    squad_catalog_path: str = Field(
        default=DEFAULT_SQUAD_CATALOG_PATH,
        description="The path of the catalogue of the simulated squad.",
    )
    command_mapping_path: str = Field(
        default=DEFAULT_COMMAND_MAPPING_PATH,
        description="The path of the catalogue that maps commands to MAVLink.",
    )
    simulated_hosts: List[str] = Field(
        default=DEFAULT_SIMULATED_HOSTS,
        description="The hosts a drone may be reached at to count as simulated.",
    )

    @field_validator(SQUAD_CATALOG_PATH_FIELD, mode=BEFORE)
    def validate_squad_catalog_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``squad_catalog_path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or the default when ``None``.

        Raises:
            SERegistryConfigInvalidSquadCatalogPath: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_SQUAD_CATALOG_PATH
        if not isinstance(value, str) or not value.strip():
            raise SERegistryConfigInvalidSquadCatalogPath(
                f"Invalid squad_catalog_path: {value!r}. Must be a non-empty string."
            )
        return value.strip()

    @field_validator(COMMAND_MAPPING_PATH_FIELD, mode=BEFORE)
    def validate_command_mapping_path(cls, value: JsonValue) -> JsonValue:
        """Validate ``command_mapping_path``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped path, or the default when ``None``.

        Raises:
            SERegistryConfigInvalidCommandMappingPath: If the value is not a non-empty string.
        """
        if value is None:
            return cls.DEFAULT_COMMAND_MAPPING_PATH
        if not isinstance(value, str) or not value.strip():
            raise SERegistryConfigInvalidCommandMappingPath(
                f"Invalid command_mapping_path: {value!r}. Must be a non-empty string."
            )
        return value.strip()

    @field_validator(SIMULATED_HOSTS_FIELD, mode=BEFORE)
    def validate_simulated_hosts(cls, value: JsonValue) -> JsonValue:
        """Validate ``simulated_hosts``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The stripped hosts, or the default when ``None``.

        Raises:
            SERegistryConfigInvalidSimulatedHosts: If the value is not a non-empty list of distinct host names.
        """
        if value is None:
            return list(cls.DEFAULT_SIMULATED_HOSTS)
        if not isinstance(value, list) or not value:
            raise SERegistryConfigInvalidSimulatedHosts(
                f"Invalid simulated_hosts: {value!r}. Must be a non-empty list of host names."
            )
        hosts: List[JsonValue] = []
        for host in value:
            if not isinstance(host, str) or not host.strip():
                raise SERegistryConfigInvalidSimulatedHosts(
                    f"Invalid simulated_hosts: {value!r}. Each host must be a non-empty string."
                )
            hosts.append(host.strip())
        if len(set(hosts)) != len(hosts):
            raise SERegistryConfigInvalidSimulatedHosts(
                f"Invalid simulated_hosts: {value!r}. Each host must appear once."
            )
        return hosts
