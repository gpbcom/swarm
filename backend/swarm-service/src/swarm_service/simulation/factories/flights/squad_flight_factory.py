from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional
from uuid import UUID

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.simulation.factories.drones.drone_service_factory import DroneServiceFactory
from swarm_service.simulation.factories.flight_factory import FlightFactory
from swarm_service.simulation.flights.squad_flight import SquadFlight


class SquadFlightFactory(FlightFactory[SquadFlight]):
    """Build the flight of the whole simulated Squad, for one Mission.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        mission_id (UUID): The Mission the Flight log belongs to.

    Notes:
        - The registry is loaded by the Drone service's factory, so a Drone on a host outside ``simulated_hosts`` stops
          the build (BR-014).
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
        """Build the Squad flight, with a Drone service of its own.

        Returns:
            SquadFlight: The new flight, with its store not yet open.
        """
        service = DroneServiceFactory(self.config).create()
        self.logger.debug("Built the flight of the Squad for Mission %s.", self.mission_id)
        return SquadFlight(service, self.mission_id, self.config.flight.status_interval_s)
