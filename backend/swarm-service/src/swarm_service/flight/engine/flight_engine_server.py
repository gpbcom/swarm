from __future__ import annotations

# Standard library imports
import asyncio
import signal
import threading
from logging import Logger, getLogger
from types import FrameType
from typing import Callable, ClassVar, Dict, Optional, Set, Tuple, Union

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_service.flight.factories.engine.flight_engine_factory import FlightEngineFactory
from swarm_web.factories.rest_server_factory import RestServerFactory


class FlightEngineServer(AsyncRunnable):
    """Runs the flight engine of an edge and the server of its live socket together, until one fails or both end.

    Attributes:
        STOP_SIGNALS (ClassVar[Tuple[signal.Signals, ...]]): The signals that ask the app to stop.
        engine_factory (FlightEngineFactory): Builds the flight engine.
        server_factory (RestServerFactory): Builds the server of the application that serves the live socket.
        previous_handlers (Dict[signal.Signals, Union[Callable, int, signal.Handlers, None]]): The handlers of the
            stop signals before ``initialize`` replaced them, put back by ``close``.
        logger (Logger): Logger instance.

    Notes:
        - One asyncio process, with one ``LiveHub`` and one ``LiveCodec`` shared by the Mission actors and the sockets:
          the app wires them into both factories.
        - The engine may end by itself, for example with no Mission to fly: the server keeps serving.
        - **A failure of the engine or of the server stops the other and is raised again**, so that the app's process
          ends with an error and is restarted.
        - The server ends when the process is asked to stop: uvicorn handles ``SIGINT`` and ``SIGTERM``, as in every
          app of Swarm, and the engine is then cancelled.
        - **A requested stop is a clean stop, and the process exits with status 0.** After its graceful stop, uvicorn
          puts back the handlers it found and raises the signal it caught again, which the default handlers turn into
          a kill (``SIGTERM``) or a ``KeyboardInterrupt`` (``SIGINT``). ``initialize`` therefore installs, before the
          server runs, a handler of each of ``STOP_SIGNALS`` that only logs the request: uvicorn puts it back and the
          signal raised again is logged instead. ``close`` puts the previous handlers back.
        - The handlers are installed from the main thread only, as uvicorn does, because Python refuses a signal
          handler set from another thread. A stop signal that arrives between ``initialize`` and the start of uvicorn
          is only logged.
        - It was the ``serve`` command of the flight engine's command line.
    """

    STOP_SIGNALS: ClassVar[Tuple[signal.Signals, ...]] = (signal.SIGINT, signal.SIGTERM)

    def __init__(
        self,
        engine_factory: FlightEngineFactory,
        server_factory: RestServerFactory,
        status_interval_s: float,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the runnable.

        Args:
            engine_factory (FlightEngineFactory): Builds the flight engine.
            server_factory (RestServerFactory): Builds the server of the live socket.
            status_interval_s (float): Seconds between two statuses.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__(status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.engine_factory = engine_factory
        self.server_factory = server_factory
        self.previous_handlers: Dict[
            signal.Signals, Union[Callable[[int, Optional[FrameType]], None], int, signal.Handlers, None]
        ] = {}

    ############################
    # Internal Helpers Methods #
    ############################

    async def _fly(self) -> None:
        """Run the flight engine until it ends."""
        async for status in self.engine_factory.create().execute():
            self.logger.debug("The flight engine is %s.", status)
        self.logger.info("The flight engine has ended.")

    async def _serve(self) -> None:
        """Run the server of the live socket until it ends."""
        async for status in self.server_factory.create().execute():
            self.logger.debug("The live server is %s.", status)
        self.logger.info("The live server has ended.")

    def _log_stop_request(self, number: int, frame: Optional[FrameType]) -> None:
        """Log a stop signal, which uvicorn has already handled or raises again after its graceful stop.

        Args:
            number (int): The number of the signal.
            frame (Optional[FrameType]): The frame the signal interrupted.
        """
        self.logger.info("The flight engine app was asked to stop by %s.", signal.Signals(number).name)

    async def _stop(self, tasks: Set[asyncio.Task[None]]) -> None:
        """Cancel the tasks still running and wait for them.

        Args:
            tasks (Set[asyncio.Task[None]]): The tasks to stop.
        """
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.debug("Stopped %d tasks.", len(tasks))

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Install the handlers of the stop signals: the engine and the server initialise themselves when they run."""
        if threading.current_thread() is not threading.main_thread():
            self.logger.debug("Not in the main thread: the handlers of the stop signals are left as they are.")
            return
        for stop in self.STOP_SIGNALS:
            self.previous_handlers[stop] = signal.signal(stop, self._log_stop_request)
        self.logger.debug("Installed the handlers of %d stop signals.", len(self.STOP_SIGNALS))

    async def run(self) -> None:
        """Run the engine and the server together until the server ends or one of them fails.

        Raises:
            Exception: Whatever the engine or the server raised, once the other is stopped.
        """
        engine = asyncio.create_task(self._fly())
        server = asyncio.create_task(self._serve())
        pending: Set[asyncio.Task[None]] = {engine, server}
        failure: Optional[BaseException] = None
        try:
            while server in pending and failure is None:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    if task.exception() is not None:
                        failure = task.exception()
                        self.logger.error("The flight engine app failed: %s.", type(failure).__name__)
                    else:
                        self.logger.debug("A task of the flight engine app has ended.")
        except BaseException as error:
            self.logger.error("The flight engine app was interrupted: %s.", type(error).__name__)
            raise
        finally:
            await self._stop(pending)
        if failure is not None:
            self.logger.error("Stopped the flight engine app after %s.", type(failure).__name__)
            raise failure

    async def close(self) -> None:
        """Put back the handlers of the stop signals: the engine and the server close themselves."""
        if not self.previous_handlers:
            self.logger.debug("No handler of a stop signal to put back.")
            return
        for stop, handler in self.previous_handlers.items():
            if handler is None:
                self.logger.debug("%s had no Python handler: its default action is put back.", stop.name)
                signal.signal(stop, signal.SIG_DFL)
            else:
                self.logger.debug("Putting back the previous handler of %s.", stop.name)
                signal.signal(stop, handler)
        self.previous_handlers = {}
        self.logger.debug("Put back the handlers of the stop signals.")
