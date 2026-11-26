from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from logging import Logger, getLogger
from typing import ClassVar, Optional

# Third-party imports
from fastapi import APIRouter, FastAPI

# First-party imports
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_api.middleware.idempotency_middleware import IdempotencyMiddleware
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.simulations.simulation_accepted import SimulationAccepted
from swarm_models.simulation.simulations.simulation_request import SimulationRequest
from swarm_service.shared.idempotency.factories.idempotency_service_factory import IdempotencyServiceFactory
from swarm_service.simulation.factories.simulations.simulation_service_factory import SimulationServiceFactory
from swarm_service.simulation.simulations.simulation_lifespan import SimulationLifespan


class SimulationRouter(APIRouter):
    """The ``/v1`` routes of the simulation domain, and the FastAPI application of the simulator app that serves them.

    Attributes:
        TITLE (ClassVar[str]): The title of the API.
        VERSION (ClassVar[str]): The version of the API.
        SIMULATIONS_PATH (ClassVar[str]): The path of the simulated flights, under ``/v1``.
        POST (ClassVar[str]): The method of the route that starts a flight.
        simulator_config (SimulatorConfig): The configuration of the simulator app.
        simulations (SimulationService): Starts the simulated flights.
        logger (Logger): Logger instance.

    Notes:
        - ``POST /v1/simulations`` starts what the ``fly`` command flew: every simulated Drone of the adapter
          registry on the square route, for the Mission of the body. It answers ``202 Accepted`` with the Mission and
          the Drones that fly, while the flight goes on in the background, and ``409 Conflict`` while another flight
          flies. The progress and the end of the flight are in the simulated Flight log of the Mission.
        - Like every ``POST`` of Swarm, it needs an ``Idempotency-Key``, so that a retried request never starts a
          second flight.
        - ``application`` wires the Commands of the bus too, through ``SimulationLifespan``, which refuses to start
          without simulated credentials (BR-014).
        - **The published document is generated from this application**: run ``uv run swarm-openapi-export`` after
          any change to a route, because ``uv run swarm-openapi-check`` fails on a stale file.
    """

    TITLE: ClassVar[str] = "Swarm simulator"
    VERSION: ClassVar[str] = "0.1.0"
    SIMULATIONS_PATH: ClassVar[str] = "/simulations"
    POST: ClassVar[str] = "POST"

    def __init__(self, config: SimulatorConfig, logger: Optional[Logger] = None) -> None:
        """Initialise the router and its route.

        Args:
            config (SimulatorConfig): The configuration of the simulator app.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.simulator_config = config
        self.simulations = SimulationServiceFactory(config).create()
        self.add_api_route(
            self.SIMULATIONS_PATH,
            self.start_simulation,
            methods=[self.POST],
            status_code=HTTPStatus.ACCEPTED,
            response_model=SimulationAccepted,
        )

    ############################
    # Publicly Exposed Methods #
    ############################

    async def start_simulation(self, request: SimulationRequest) -> SimulationAccepted:
        """Start the simulated flight of the Squad for a Mission.

        Args:
            request (SimulationRequest): The Mission to fly for.

        Returns:
            SimulationAccepted: The Mission and the Drones that fly.
        """
        self.logger.debug("A simulated flight is asked for Mission %s.", request.mission_id)
        return await self.simulations.launch(request)

    def application(self) -> FastAPI:
        """Build the application of the simulator app.

        Returns:
            FastAPI: The application, with the REST conventions of Swarm, this router and the Commands of the bus.
        """
        self.logger.debug("Building the simulator application.")
        app = ProblemHandlers().application(self.TITLE, self.VERSION, [self])
        app.add_middleware(
            IdempotencyMiddleware, service=IdempotencyServiceFactory(self.simulator_config.rest).create()
        )
        self.logger.debug("The problem handlers and the idempotency middleware are installed.")
        app.router.lifespan_context = SimulationLifespan(self.simulator_config, self.simulations).lifespan
        self.logger.debug("The Commands of the bus are wired on the simulator application.")
        return app
