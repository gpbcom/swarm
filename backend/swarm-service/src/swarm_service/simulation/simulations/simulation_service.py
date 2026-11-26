from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import Optional

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.simulations.exceptions import SESimulationRunningError
from swarm_models.simulation.simulations.simulation_accepted import SimulationAccepted
from swarm_models.simulation.simulations.simulation_request import SimulationRequest
from swarm_service.simulation.factories.flights.squad_flight_factory import SquadFlightFactory
from swarm_service.simulation.flights.squad_flight import SquadFlight


class SimulationService:
    """Starts the simulated flights of the Squad, one at a time, each for one Mission.

    Attributes:
        config (SimulatorConfig): The configuration of the Simulator.
        flight (Optional[SquadFlight]): The Squad flight that flies now, or flew last.
        task (Optional[asyncio.Task[None]]): The task that reads the statuses of the flight while it flies.
        logger (Logger): Logger instance.

    Notes:
        - It flies what the ``fly`` command flew: every Drone of the adapter registry on the square route, with the
          Flight log of the Mission marked simulated (BR-014). The outcome of each Drone is logged when the flight
          ends, where ``fly`` printed it.
        - **One flight at a time**: a request while a flight flies raises ``SESimulationRunningError`` (409), because
          two flights would send two routes to the same Drones.
        - The flight is an ``AsyncRunnable``: the task reads its statuses and logs them, and ``close`` cancels it.
    """

    def __init__(self, config: SimulatorConfig, logger: Optional[Logger] = None) -> None:
        """Create the service, with no flight yet.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.flight: Optional[SquadFlight] = None
        self.task: Optional[asyncio.Task[None]] = None

    ############################
    # Internal Helpers Methods #
    ############################

    async def _fly(self, flight: SquadFlight) -> None:
        """Read the statuses of a flight until it ends, then log the outcome of each Drone.

        Args:
            flight (SquadFlight): The Squad flight.
        """
        try:
            async for status in flight.execute():
                self.logger.debug("The Squad flight of Mission %s is %s.", flight.mission_id, status)
        except Exception as error:  # noqa: BLE001
            self.logger.error("The Squad flight of Mission %s failed: %s.", flight.mission_id, type(error).__name__)
            return
        for outcome in flight.outcomes:
            self.logger.info(
                "Drone %s of kind %s: completed %s, %d waypoints, %.1f s.",
                outcome.drone_id,
                outcome.kind.value,
                outcome.completed,
                outcome.waypoints_reached,
                outcome.elapsed_s,
            )
        if flight.all_completed:
            self.logger.info("Every Drone completed its route for Mission %s.", flight.mission_id)
        else:
            self.logger.warning("At least one Drone did not complete its route for Mission %s.", flight.mission_id)

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def flying(self) -> bool:
        """Whether a flight flies now."""
        return self.task is not None and not self.task.done()

    async def launch(self, request: SimulationRequest) -> SimulationAccepted:
        """Start the simulated flight of the Squad for a Mission, in the background.

        Args:
            request (SimulationRequest): The Mission to fly for.

        Returns:
            SimulationAccepted: The Mission and the Drones that fly.

        Raises:
            SESimulationRunningError: When a flight still flies.
        """
        if self.flying:
            self.logger.error("Refused a flight for Mission %s: another one flies.", request.mission_id)
            raise SESimulationRunningError("A simulated flight is already flying. Wait for it to end.")
        flight = SquadFlightFactory(self.config, request.mission_id).create()
        drone_ids = [drone.drone_id for drone in flight.service.registry.drones()]
        self.flight = flight
        self.task = asyncio.create_task(self._fly(flight))
        self.logger.info("Started the flight of %d Drones for Mission %s.", len(drone_ids), request.mission_id)
        return SimulationAccepted(mission_id=request.mission_id, drone_ids=drone_ids)

    async def close(self) -> None:
        """Stop the flight that flies, if any, and wait until it is closed."""
        task, self.task = self.task, None
        if task is None or task.done():
            self.logger.debug("No flight to stop.")
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            self.logger.debug("The flight was cancelled.")
        self.logger.info("Stopped the flight that was flying.")
