from __future__ import annotations

# Standard library imports
import asyncio
import signal
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, Optional, Tuple

# Third-party imports
import uvloop
from fastapi import FastAPI

# First-party imports
from flight_engine.api.cli.commands.command import Command
from flight_engine.api.cli.conf_locator import ConfLocator
from flight_engine.api.factories.live.live_server_factory import LiveServerFactory
from flight_engine.api.live.live_endpoint import LiveEndpoint
from flight_engine.models.config.flight_engine_config import FlightEngineConfig
from flight_engine.models.missions.mission_catalog import MissionCatalog
from flight_engine.models.telemetry.drone_state_catalog import DroneStateCatalog
from flight_engine.service.factories.engine.flight_engine_factory import FlightEngineFactory
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub


class ServeCommand(Command):
    """Runs the flight engine and its local live server together until SIGINT or SIGTERM.

    Attributes:
        STOP_SIGNALS (ClassVar[Tuple[signal.Signals, ...]]): The signals that stop the command.
        config_path (Path): The configuration file of the service.
        config (Optional[FlightEngineConfig]): The configuration, once ``initialize`` has loaded it.
        catalog (Optional[MissionCatalog]): The Missions to fly, once loaded.
        states (Optional[DroneStateCatalog]): The Drone states, once loaded.
        exit_code (int): 0 after a stop asked by a signal, 1 when the engine or the server failed.
        logger (Logger): Logger instance.

    Notes:
        - One asyncio process on uvloop, with one ``LiveHub`` and one ``LiveCodec`` shared by the actors and the
          sockets.
        - The engine may end by itself, for example with no Mission to fly: the server keeps serving.
        - **A failure of the engine or the server stops both and sets the exit code to 1.**
    """

    STOP_SIGNALS: ClassVar[Tuple[signal.Signals, ...]] = (signal.SIGINT, signal.SIGTERM)

    def __init__(self, config_path: Path, logger: Optional[Logger] = None) -> None:
        """Initialise the command.

        Args:
            config_path (Path): The configuration file of the service.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.config_path = config_path
        self.config: Optional[FlightEngineConfig] = None
        self.catalog: Optional[MissionCatalog] = None
        self.states: Optional[DroneStateCatalog] = None

    ############################
    # Internal Helpers Methods #
    ############################

    async def _fly(self, factory: FlightEngineFactory, stop: asyncio.Event) -> None:
        """Run the engine, and ask to stop if it fails.

        Args:
            factory (FlightEngineFactory): Builds the engine.
            stop (asyncio.Event): Set when the engine fails.
        """
        try:
            async for status in factory.create().execute():
                self.logger.debug("The flight engine is %s.", status)
        except Exception as error:  # noqa: BLE001
            self.logger.error("The flight engine failed: %s.", type(error).__name__)
            self.exit_code = 1
            stop.set()
            return
        self.logger.info("The flight engine has ended.")

    async def _listen(self, factory: LiveServerFactory, stop: asyncio.Event) -> None:
        """Run the live server, and ask to stop when it ends.

        Args:
            factory (LiveServerFactory): Builds the server.
            stop (asyncio.Event): Set when the server ends.
        """
        try:
            async for status in factory.create().execute():
                self.logger.debug("The live server is %s.", status)
        except Exception as error:  # noqa: BLE001
            self.logger.error("The live server failed: %s.", type(error).__name__)
            self.exit_code = 1
        finally:
            stop.set()

    async def _serve(self) -> None:
        """Run the engine and the server together until a signal or a failure."""
        if self.config is None or self.catalog is None or self.states is None:
            self.logger.error("The command was run before it was initialised.")
            self.exit_code = 1
            return
        hub, codec = LiveHub(), LiveCodec()
        app = FastAPI()
        app.include_router(LiveEndpoint(hub, codec, self.config.live).router())
        engine_factory = FlightEngineFactory(self.config, self.catalog, self.states, hub, codec)
        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for number in self.STOP_SIGNALS:
            loop.add_signal_handler(number, stop.set)
        tasks = [
            asyncio.create_task(self._fly(engine_factory, stop)),
            asyncio.create_task(self._listen(LiveServerFactory(app, self.config.live), stop)),
        ]
        await stop.wait()
        self.logger.info("Stopping the flight engine and the live server.")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        for number in self.STOP_SIGNALS:
            loop.remove_signal_handler(number)

    ############################
    # Publicly Exposed Methods #
    ############################

    def initialize(self) -> None:
        """Load the configuration and the two catalogues."""
        locator = ConfLocator()
        self.config = FlightEngineConfig.load(locator.locate(self.config_path))
        self.catalog = MissionCatalog.load(locator.locate(Path(self.config.missions_catalog_path)))
        self.states = DroneStateCatalog.load(locator.locate(Path(self.config.drone_states_catalog_path)))
        self.logger.info("Loaded %d Missions.", len(self.catalog.missions))

    def run(self) -> None:
        """Serve with uvloop until the command is stopped."""
        uvloop.run(self._serve())

    def close(self) -> None:
        """Release nothing: the engine and the server close themselves."""
        self.logger.debug("Nothing to release after serving.")
