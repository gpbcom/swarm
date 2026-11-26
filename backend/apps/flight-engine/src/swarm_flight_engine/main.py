from __future__ import annotations

# Standard library imports
import asyncio
from logging import getLogger

# Third-party imports
import uvloop

# First-party imports
from swarm_api.v1.flight.flight_engine_router import FlightEngineRouter
from swarm_logging.configurators.logging_configurator import LoggingConfigurator
from swarm_logging.models.logging_config import LoggingConfig
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_service.flight.factories.engine.flight_engine_server_factory import FlightEngineServerFactory
from swarm_web.factories.async_runnable_runner_factory import AsyncRunnableRunnerFactory


def main() -> None:
    """Read the configuration of the flight engine app, configure logging, then fly and serve until it is stopped.

    Notes:
        - The app's folder is ``SWARM_APP_ROOT``, which the image sets, or the current folder.
        - Logging is configured once, here at the entry point.
        - The event loop is uvloop's: the engine and its live socket run in one asyncio process.
        - **``SIGINT`` and ``SIGTERM`` stop the app cleanly and the process exits with status 0**, because
          ``FlightEngineServer`` logs the signal that uvicorn raises again after its graceful stop. A failure of the
          engine or of the server is raised from here, and the process exits with an error.
    """
    folder = FlightEngineConfig.conf_folder()
    config = FlightEngineConfig.load(folder / FlightEngineConfig.APP_FILE)
    LoggingConfigurator(LoggingConfig(path=str(folder / FlightEngineConfig.LOGGER_FILE))).configure()
    getLogger(__name__).info("Serving the flight engine app on port %d.", config.live.port)
    router = FlightEngineRouter(config)
    server = FlightEngineServerFactory(config, router.application(), router.hub, router.codec).create()
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    AsyncRunnableRunnerFactory(server).create().execute()
