from __future__ import annotations

# Standard library imports
import asyncio
from logging import Logger, getLogger
from typing import ClassVar, Optional
from uuid import UUID

# First-party imports
from simulator.api.cli.commands.command import Command
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.service.factories.flights.squad_flight_factory import SquadFlightFactory
from simulator.service.flights.squad_flight import SquadFlight


class FlyCommand(Command):
    """Command that flies the simulated Squad once and prints one line per Drone.

    Attributes:
        EXIT_INCOMPLETE (int): The exit code when a Drone did not complete its route.
        OUTCOME_LINE (str): The line printed for the outcome of one Drone.
        config (SimulatorConfig): The configuration of the Simulator.
        mission_id (UUID): The Mission the Flight log belongs to.
        flight (Optional[SquadFlight]): The Squad flight, once ``initialize`` has run.
        exit_code (int): ``0`` when every Drone completed its route, otherwise ``1``.
        logger (Logger): Logger instance.

    Notes:
        - Only ``api/cli/`` prints, because this output is for the person at the terminal.
    """

    EXIT_INCOMPLETE: ClassVar[int] = 1
    OUTCOME_LINE: ClassVar[str] = (
        "drone={drone_id} kind={kind} completed={completed} waypoints={waypoints} elapsed_s={elapsed:.1f}"
    )

    def __init__(self, config: SimulatorConfig, mission_id: UUID, logger: Optional[Logger] = None) -> None:
        """Prepare the command.

        Args:
            config (SimulatorConfig): The configuration of the Simulator.
            mission_id (UUID): The Mission the Flight log belongs to.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config = config
        self.mission_id = mission_id
        self.flight: Optional[SquadFlight] = None

    ############################
    # Internal Helpers Methods #
    ############################

    async def _fly(self, flight: SquadFlight) -> None:
        """Read the statuses of the flight until it ends.

        Args:
            flight (SquadFlight): The Squad flight.
        """
        async for status in flight.execute():
            self.logger.debug("The Squad flight is %s.", status)

    ############################
    # Publicly Exposed Methods #
    ############################

    def initialize(self) -> None:
        """Build the Squad flight."""
        self.flight = SquadFlightFactory(self.config, self.mission_id).create()

    def run(self) -> None:
        """Fly the Squad, print each outcome and set the exit code."""
        flight = self.flight
        if flight is None:
            self.logger.error("There is no Squad flight to fly.")
            self.exit_code = self.EXIT_INCOMPLETE
            return
        asyncio.run(self._fly(flight))
        for outcome in flight.outcomes:
            print(
                self.OUTCOME_LINE.format(
                    drone_id=outcome.drone_id,
                    kind=outcome.kind.value,
                    completed=outcome.completed,
                    waypoints=outcome.waypoints_reached,
                    elapsed=outcome.elapsed_s,
                )
            )
        if flight.all_completed:
            self.logger.info("Every Drone completed its route.")
            self.exit_code = 0
        else:
            self.logger.warning("At least one Drone did not complete its route.")
            self.exit_code = self.EXIT_INCOMPLETE

    def close(self) -> None:
        """Release nothing: the Squad flight closes its own store."""
        self.logger.debug("Nothing to release after the flight.")
