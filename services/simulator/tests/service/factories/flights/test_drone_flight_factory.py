from __future__ import annotations

# Standard library imports
from pathlib import Path
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from services.simulator.tests.helpers import MISSION_ID, a_registered_drone
from services.simulator.tests.stand_in_drone import StandInDrone
from simulator.clients.mavlink.mavlink_drone_client import MavlinkDroneClient
from simulator.models.config.flight_config import FlightConfig
from simulator.models.config.route_config import RouteConfig
from simulator.service.factories.flight_factory import FlightFactory
from simulator.service.factories.flights.drone_flight_factory import DroneFlightFactory
from simulator.service.flights.drone_flight import DroneFlight
from simulator.service.routes.square_route_builder import SquareRouteBuilder
from simulator.storage.edge.flight_log_store import FlightLogStore
from swarm_lifecycle.models.enums import RunnableStatus

STORE_FILE = "flight_log.sqlite3"


class TestDroneFlightFactory:
    @pytest.fixture
    def config(self) -> FlightConfig:
        return FlightConfig(heartbeat_timeout_s=1.0, arm_timeout_s=2.0, route_timeout_s=1.0, status_interval_s=0.1)

    def a_factory(self, stand_in: StandInDrone, tmp_path: Path, config: FlightConfig) -> DroneFlightFactory:
        return DroneFlightFactory(
            a_registered_drone(stand_in),
            UUID(str(MISSION_ID)),
            SquareRouteBuilder(RouteConfig()),
            FlightLogStore(str(tmp_path / STORE_FILE)),
            config,
        )

    def test_it_is_a_flight_factory(self, stand_in_drone: StandInDrone, tmp_path: Path, config: FlightConfig) -> None:
        assert isinstance(self.a_factory(stand_in_drone, tmp_path, config), FlightFactory)

    def test_it_creates_a_drone_flight_with_its_own_client(
        self, stand_in_drone: StandInDrone, tmp_path: Path, config: FlightConfig
    ) -> None:
        factory = self.a_factory(stand_in_drone, tmp_path, config)
        first = factory.create()
        second = factory.create()
        assert isinstance(first, DroneFlight)
        assert isinstance(first.client, MavlinkDroneClient)
        assert first.client is not second.client
        assert first.drone == a_registered_drone(stand_in_drone)
        assert first.status_interval_s == config.status_interval_s

    async def test_the_created_flight_flies_the_route(
        self, stand_in_drone: StandInDrone, tmp_path: Path, config: FlightConfig
    ) -> None:
        flight = self.a_factory(stand_in_drone, tmp_path, config).create()
        flight.store.open()
        statuses = [status async for status in flight.execute()]
        flight.store.close()
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert flight.outcome is not None
        assert flight.outcome.completed is True
