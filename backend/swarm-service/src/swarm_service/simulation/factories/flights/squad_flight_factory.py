from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from pathlib import Path
from typing import List, Optional
from uuid import UUID

# First-party imports
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.models.registry.simulated_squad_catalog import SimulatedSquadCatalog
from simulator.service.factories.flight_factory import FlightFactory
from simulator.service.factories.flights.drone_flight_factory import DroneFlightFactory
from simulator.service.flights.drone_flight import DroneFlight
from simulator.service.flights.squad_flight import SquadFlight
from simulator.service.registry.adapter_registry import AdapterRegistry
from simulator.service.routes.square_route_builder import SquareRouteBuilder
from simulator.storage.edge.flight_log_store import FlightLogStore


class SquadFlightFactory(FlightFactory[SquadFlight]):
    """Build the flight of the whole simulated Squad.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        mission_id (UUID): The Mission the Flight log belongs to.

    Notes:
        - The registry is loaded here, so a Drone on a host outside ``simulated_hosts`` stops the build (BR-014).
    """

    def __init__(self, config: SimulatorConfig, mission_id: UUID, logger: Optional[Logger] = None) -> None:
        """Create the factory.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            mission_id (UUID): The Mission the Flight log belongs to.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.mission_id = mission_id

    ############################
    # Internal Helpers Methods #
    ############################

    def _build(self) -> SquadFlight:
        """Build the Squad flight, with one Drone flight per registered Drone.

        Returns:
            SquadFlight: The new flight, with its store not yet open.
        """
        squad = SimulatedSquadCatalog.load(Path(self.config.registry.squad_catalog_path))
        registry = AdapterRegistry(self.config.registry.simulated_hosts)
        registry.load(squad)
        builder = SquareRouteBuilder(self.config.route)
        store = FlightLogStore(self.config.flight_log_path)
        flights: List[DroneFlight] = []
        for drone in registry.drones():
            factory = DroneFlightFactory(drone, self.mission_id, builder, store, self.config.flight)
            flights.append(factory.create())
        self.logger.debug("Built the flights of %d Drones.", len(flights))
        return SquadFlight(flights, store, self.config.flight.status_interval_s)
