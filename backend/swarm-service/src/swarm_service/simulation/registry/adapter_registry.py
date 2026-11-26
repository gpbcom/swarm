from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Dict, List, Optional
from uuid import UUID

# First-party imports
from simulator.models.registry.exceptions import (
    SEAdapterRegistryDuplicateDroneError,
    SEAdapterRegistryHostRefusedError,
    SEAdapterRegistryUnknownDroneError,
)
from simulator.models.registry.registered_drone import RegisteredDrone
from simulator.models.registry.simulated_squad_catalog import SimulatedSquadCatalog


class AdapterRegistry:
    """The simulated Drones the Simulator may address, keyed by Drone id.

    Attributes:
        simulated_hosts (List[str]): The hosts a simulated Drone may be reached at.
        drones_by_id (Dict[UUID, RegisteredDrone]): The registered Drones, in insertion order.
        logger (Logger): Logger instance.

    Notes:
        - **This is how the Simulator cannot address a real Drone (BR-014): every client the Simulator opens comes
          from ``resolve()``, and the registry only holds simulated Drones on an allowed host.**
        - A Drone on a host outside the list is refused before anything is stored.
    """

    def __init__(self, simulated_hosts: List[str], logger: Optional[Logger] = None) -> None:
        """Create an empty registry.

        Args:
            simulated_hosts (List[str]): The hosts a simulated Drone may be reached at.
            logger (Optional[Logger]): Logger instance.
        """
        self.simulated_hosts = list(simulated_hosts)
        self.drones_by_id: Dict[UUID, RegisteredDrone] = {}
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    def register(self, drone: RegisteredDrone) -> None:
        """Register one simulated Drone.

        Args:
            drone (RegisteredDrone): The Drone to register.

        Raises:
            SEAdapterRegistryHostRefusedError: If the host is not a simulated host.
            SEAdapterRegistryDuplicateDroneError: If the Drone id is already registered.
        """
        if drone.host not in self.simulated_hosts:
            self.logger.error("Refused Drone %s: host %s is not simulated.", drone.drone_id, drone.host)
            raise SEAdapterRegistryHostRefusedError(
                f"Invalid host: {drone.host!r}. Must be one of {self.simulated_hosts}."
            )
        if drone.drone_id in self.drones_by_id:
            self.logger.error("Refused Drone %s: already registered.", drone.drone_id)
            raise SEAdapterRegistryDuplicateDroneError(
                f"Invalid drone: {str(drone.drone_id)!r}. Must be registered once."
            )
        self.drones_by_id[drone.drone_id] = drone
        self.logger.debug("Registered Drone %s at %s:%d.", drone.drone_id, drone.host, drone.port)

    def load(self, catalog: SimulatedSquadCatalog) -> None:
        """Register every Drone of a catalogue.

        Args:
            catalog (SimulatedSquadCatalog): The catalogue to load.
        """
        for drone in catalog.drones:
            self.register(drone)
        self.logger.info("Loaded %d Drones into the registry.", len(catalog.drones))

    def resolve(self, drone_id: UUID) -> RegisteredDrone:
        """Find a registered Drone.

        Args:
            drone_id (UUID): The Drone id.

        Returns:
            RegisteredDrone: The Drone.

        Raises:
            SEAdapterRegistryUnknownDroneError: If the Drone id is not registered.
        """
        drone = self.drones_by_id.get(drone_id)
        if drone is None:
            self.logger.error("Unknown Drone %s.", drone_id)
            raise SEAdapterRegistryUnknownDroneError(f"Invalid drone: {str(drone_id)!r}. Must be registered.")
        self.logger.debug("Resolved Drone %s.", drone_id)
        return drone

    def contains(self, drone_id: UUID) -> bool:
        """Tell whether a Drone is registered.

        Args:
            drone_id (UUID): The Drone id.

        Returns:
            bool: True when the Drone is registered.
        """
        known = drone_id in self.drones_by_id
        self.logger.debug("Drone %s registered: %s.", drone_id, known)
        return known

    def drones(self) -> List[RegisteredDrone]:
        """List the registered Drones.

        Returns:
            List[RegisteredDrone]: The Drones, in registration order.
        """
        self.logger.debug("Listing %d Drones.", len(self.drones_by_id))
        return list(self.drones_by_id.values())
