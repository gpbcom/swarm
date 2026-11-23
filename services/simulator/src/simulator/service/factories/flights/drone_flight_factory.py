from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional
from uuid import UUID

# First-party imports
from simulator.clients.mavlink.mavlink_drone_client import MavlinkDroneClient
from simulator.models.config.flight_config import FlightConfig
from simulator.models.registry.registered_drone import RegisteredDrone
from simulator.service.factories.flight_factory import FlightFactory
from simulator.service.flights.drone_flight import DroneFlight
from simulator.service.routes.square_route_builder import SquareRouteBuilder
from simulator.storage.edge.flight_log_store import FlightLogStore


class DroneFlightFactory(FlightFactory[DroneFlight]):
    """Build the flight of one Drone, with its own MAVLink client.

    Attributes:
        drone (RegisteredDrone): The Drone to fly.
        mission_id (UUID): The Mission the Flight log belongs to.
        builder (SquareRouteBuilder): Builds the route.
        store (FlightLogStore): The Flight log, which the caller opens.
        config (FlightConfig): The timings of a flight.
    """

    def __init__(
        self,
        drone: RegisteredDrone,
        mission_id: UUID,
        builder: SquareRouteBuilder,
        store: FlightLogStore,
        config: FlightConfig,
        logger: Optional[Logger] = None,
    ) -> None:
        """Create the factory.

        Args:
            drone (RegisteredDrone): The Drone to fly.
            mission_id (UUID): The Mission the Flight log belongs to.
            builder (SquareRouteBuilder): Builds the route.
            store (FlightLogStore): The Flight log, which the caller opens.
            config (FlightConfig): The timings of a flight.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.drone = drone
        self.mission_id = mission_id
        self.builder = builder
        self.store = store
        self.config = config

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> DroneFlight:
        """Build a flight with a new client.

        Returns:
            DroneFlight: The new flight.
        """
        client = MavlinkDroneClient(self.drone, self.config)
        return DroneFlight(self.drone, self.mission_id, client, self.builder, self.store, self.config)
