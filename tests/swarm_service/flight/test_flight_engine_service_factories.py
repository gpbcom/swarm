from __future__ import annotations

# Standard library imports
import importlib
import inspect

# Third-party imports
import pytest

# First-party imports
from swarm_lifecycle.factories.async_runnable_factory import AsyncRunnableFactory
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.flight.missions.mission_catalog import MissionCatalog
from swarm_models.flight.telemetry.drone_state_catalog import DroneStateCatalog
from swarm_service.flight.engine.flight_engine import FlightEngine
from swarm_service.flight.factories.engine_factory import EngineFactory
from swarm_service.flight.factories.missions.mission_actor_factory import MissionActorFactory
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.live_codec import LiveCodec


class TestFlightEngineServiceFactories:
    FACTORY_MODULE = "swarm_service.flight.factories.engine.flight_engine_factory"
    FACTORY_CLASS = "FlightEngineFactory"
    SWARM_CORE = "swarm_core"

    @pytest.mark.parametrize("factory", [EngineFactory, MissionActorFactory])
    def test_the_abstract_factories_build_async_runnables_and_cannot_be_created(self, factory: type) -> None:
        assert issubclass(factory, AsyncRunnableFactory)
        assert inspect.isabstract(factory)

    def test_the_flight_engine_factory_builds_a_flight_engine(
        self, flight_engine_config: FlightEngineConfig, states: DroneStateCatalog
    ) -> None:
        pytest.importorskip(self.SWARM_CORE)
        module = importlib.import_module(self.FACTORY_MODULE)
        factory_class = getattr(module, self.FACTORY_CLASS)
        factory = factory_class(flight_engine_config, MissionCatalog(), states, LiveHub(), LiveCodec())
        assert isinstance(factory, EngineFactory)
        assert isinstance(factory.create(), FlightEngine)
