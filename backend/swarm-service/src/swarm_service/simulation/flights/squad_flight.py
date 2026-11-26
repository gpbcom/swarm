from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import List, Optional
from uuid import UUID

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_models.simulation.flights.exceptions import SEDroneFlightError
from swarm_models.simulation.flights.flight_outcome import FlightOutcome
from swarm_models.simulation.registry.registered_drone import RegisteredDrone
from swarm_service.simulation.drones.drone_service import DroneService


class SquadFlight(AsyncRunnable):
    """Fly every Drone of a simulated Squad at once, for one Mission.

    Attributes:
        service (DroneService): Flies each Drone of its adapter registry and writes the shared Flight log.
        mission_id (UUID): The Mission the Flight log belongs to.
        outcomes (List[FlightOutcome]): The outcome of each flight that ended, once the Squad has flown.

    Notes:
        - **A Drone that fails does not stop the others**: its error is logged at ``WARNING`` and its outcome is
          incomplete.
        - The Squad opens the service, and with it the shared Flight log store, and closes it.
    """

    def __init__(
        self,
        service: DroneService,
        mission_id: UUID,
        status_interval_s: float,
        logger: Optional[Logger] = None,
    ) -> None:
        """Create the Squad flight.

        Args:
            service (DroneService): Flies the Drones of its adapter registry.
            mission_id (UUID): The Mission the Flight log belongs to.
            status_interval_s (float): Seconds between two statuses.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.service = service
        self.mission_id = mission_id
        self.outcomes: List[FlightOutcome] = []

    ############################
    # Internal Helpers Methods #
    ############################

    async def _fly(self, drone: RegisteredDrone) -> None:
        """Fly one Drone to the end, whatever happens to it.

        Args:
            drone (RegisteredDrone): The Drone.
        """
        try:
            await self.service.fly(drone, self.mission_id)
        except SEDroneFlightError as error:
            self.logger.warning("Drone %s did not complete: %s.", drone.drone_id, type(error).__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def all_completed(self) -> bool:
        """Whether there is at least one outcome and every one is complete."""
        if not self.outcomes:
            return False
        return all(outcome.completed for outcome in self.outcomes)

    async def initialize(self) -> None:
        """Open the Drone service and its Flight log store."""
        await self.service.open()

    async def run(self) -> None:
        """Fly every Drone of the registry concurrently and collect the outcomes."""
        drones = self.service.registry.drones()
        await asyncio.gather(*(self._fly(drone) for drone in drones))
        self.outcomes = [
            self.service.outcomes[drone.drone_id] for drone in drones if drone.drone_id in self.service.outcomes
        ]
        completed = sum(1 for outcome in self.outcomes if outcome.completed)
        self.logger.info("%d of %d Drones completed their route.", completed, len(drones))

    async def close(self) -> None:
        """Close the Drone service and its Flight log store."""
        await self.service.close()
