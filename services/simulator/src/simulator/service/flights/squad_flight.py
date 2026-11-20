from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import List, Optional

# First-party imports
from simulator.models.flights.exceptions import SEDroneFlightError
from simulator.models.flights.flight_outcome import FlightOutcome
from simulator.service.flights.drone_flight import DroneFlight
from simulator.storage.edge.flight_log_store import FlightLogStore
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable


class SquadFlight(AsyncRunnable):
    """Fly every Drone of a simulated Squad at once.

    Attributes:
        flights (List[DroneFlight]): The flights, one per Drone.
        store (FlightLogStore): The Flight log shared by every flight.
        outcomes (List[FlightOutcome]): The outcome of each flight that ended, once the Squad has flown.

    Notes:
        - **A Drone that fails does not stop the others**: its error is logged at ``WARNING`` and its outcome is
          incomplete.
        - The Squad opens the shared store and closes it, and its flights only write to it.
    """

    def __init__(
        self,
        flights: List[DroneFlight],
        store: FlightLogStore,
        status_interval_s: float,
        logger: Optional[Logger] = None,
    ) -> None:
        """Create the Squad flight.

        Args:
            flights (List[DroneFlight]): The flights, one per Drone.
            store (FlightLogStore): The Flight log shared by every flight.
            status_interval_s (float): Seconds between two statuses.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.flights = flights
        self.store = store
        self.outcomes: List[FlightOutcome] = []

    ############################
    # Internal Helpers Methods #
    ############################

    async def _fly(self, flight: DroneFlight) -> None:
        """Fly one Drone to the end, whatever happens to it.

        Args:
            flight (DroneFlight): The flight.
        """
        try:
            async for _ in flight.execute():
                self.logger.debug("Drone %s is %s.", flight.drone.drone_id, flight.status)
        except SEDroneFlightError as error:
            self.logger.warning("Drone %s did not complete: %s.", flight.drone.drone_id, type(error).__name__)

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
        """Open the shared Flight log store."""
        self.store.open()

    async def run(self) -> None:
        """Fly every Drone concurrently and collect the outcomes."""
        await asyncio.gather(*(self._fly(flight) for flight in self.flights))
        self.outcomes = [flight.outcome for flight in self.flights if flight.outcome is not None]
        completed = sum(1 for outcome in self.outcomes if outcome.completed)
        self.logger.info("%d of %d Drones completed their route.", completed, len(self.flights))

    async def close(self) -> None:
        """Close the shared Flight log store."""
        self.store.close()
