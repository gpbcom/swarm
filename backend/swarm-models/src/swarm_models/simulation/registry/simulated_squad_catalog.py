from __future__ import annotations

# Standard library imports
from typing import ClassVar, List, Literal, Self, Set, Tuple
from uuid import UUID

# Third-party imports
from pydantic import Field, JsonValue, field_validator, model_validator

# First-party imports
from simulator.models.registry.exceptions import (
    SESimulatedSquadCatalogDuplicateDrone,
    SESimulatedSquadCatalogDuplicateEndpoint,
    SESimulatedSquadCatalogInvalidDrones,
    SESimulatedSquadCatalogUnreadable,
)
from simulator.models.registry.registered_drone import RegisteredDrone
from swarm_catalog.models.yaml_catalog import YamlCatalog


class SimulatedSquadCatalog(YamlCatalog):
    """The catalogue of the simulated Drones the adapter registry knows.

    Attributes:
        UNREADABLE (type[Exception]): The exception raised when the file cannot be read.
        DRONES_FIELD (str): The name of the ``drones`` field.
        BEFORE (str): The validator mode that runs before Pydantic's own validation.
        drones (List[RegisteredDrone]): The simulated Drones.

    Notes:
        - A Drone id, and a host with its port, appear once.
    """

    UNREADABLE: ClassVar[type[Exception]] = SESimulatedSquadCatalogUnreadable
    DRONES_FIELD: ClassVar[str] = "drones"
    BEFORE: ClassVar[Literal["before"]] = "before"

    drones: List[RegisteredDrone] = Field(description="The simulated Drones.")

    @field_validator(DRONES_FIELD, mode=BEFORE)
    def validate_drones(cls, value: JsonValue) -> JsonValue:
        """Validate ``drones``.

        Args:
            value (JsonValue): The raw input.

        Returns:
            JsonValue: The list of Drones, left to Pydantic to build.

        Raises:
            SESimulatedSquadCatalogInvalidDrones: If the value is not a non-empty list.
        """
        if not isinstance(value, list) or not value:
            raise SESimulatedSquadCatalogInvalidDrones(f"Invalid drones: {value!r}. Must be a non-empty list.")
        return value

    @model_validator(mode="after")
    def validate_unique(self) -> Self:
        """Check that no Drone id and no endpoint is used twice.

        Returns:
            Self: The catalogue.

        Raises:
            SESimulatedSquadCatalogDuplicateDrone: If two Drones share an id.
            SESimulatedSquadCatalogDuplicateEndpoint: If two Drones share a host and a port.
        """
        ids: Set[UUID] = set()
        endpoints: Set[Tuple[str, int]] = set()
        for drone in self.drones:
            if drone.drone_id in ids:
                raise SESimulatedSquadCatalogDuplicateDrone(
                    f"Invalid drones: {str(drone.drone_id)!r}. Must appear once."
                )
            ids.add(drone.drone_id)
            endpoint = (drone.host, drone.port)
            if endpoint in endpoints:
                raise SESimulatedSquadCatalogDuplicateEndpoint(
                    f"Invalid drones: {drone.host}:{drone.port}. Must be reached at one endpoint each."
                )
            endpoints.add(endpoint)
        return self
