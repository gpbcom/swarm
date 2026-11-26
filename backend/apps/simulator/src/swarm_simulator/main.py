from __future__ import annotations

# Standard library imports
from logging import getLogger

# First-party imports
from swarm_api.v1.simulation.simulation_router import SimulationRouter
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.simulation.factories.servers.simulator_server_factory import SimulatorServerFactory
from swarm_web.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory


def main() -> None:
    """Read the configuration of the simulator app, configure logging, then serve and respond until it is stopped.

    Notes:
        - The app's folder is ``SWARM_APP_ROOT``, which the image sets, or the current folder.
        - Logging is configured once, here at the entry point.
        - The app serves ``POST /v1/simulations`` and, beside its application, answers the Commands of the bus.
          **It does not start without simulated credentials** (BR-014): the app stops with an error before anything
          connects or serves.
        - **A Command responder that cannot start or fails, such as on a NATS server that cannot be reached, stops
          the app with an error**, raised from here, so that the process exits with a non-zero status and is
          restarted.
    """
    folder = SimulatorConfig.conf_folder()
    config = SimulatorConfig.load(folder / SimulatorConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(folder / SimulatorConfig.LOGGER_FILE))).configure()
    getLogger(__name__).info("Serving the simulator app on port %d.", config.rest.port)
    server = SimulatorServerFactory(config, SimulationRouter(config).application()).create()
    AsyncRunnableRunnerFactory(server).create().execute()
