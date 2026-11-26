from __future__ import annotations

# Standard library imports
from functools import partial
from pathlib import Path
from typing import List
from uuid import UUID

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_service.simulation.drones.drone_service import DroneService
from swarm_service.simulation.factories.flight_factory import FlightFactory
from swarm_service.simulation.factories.flights.squad_flight_factory import SquadFlightFactory
from swarm_service.simulation.flights.squad_flight import SquadFlight
from tests.fakes.mavlink.helpers import DRONE_IDS, MISSION_ID, a_registered_drone
from tests.fakes.mavlink.stand_in_drone import StandInDrone
from tests.fakes.mavlink.stand_in_drones import StandInDrones

SQUAD_SIZE = 2


class TestSquadFlightFactory:
    def a_config(self, stand_ins: List[StandInDrone], app_config: partial[Path]) -> SimulatorConfig:
        drones = [a_registered_drone(stand_in, index) for index, stand_in in enumerate(stand_ins)]
        return SimulatorConfig.load(app_config(drones))

    def test_it_is_a_flight_factory(self, stand_in_drone: StandInDrone, app_config: partial[Path]) -> None:
        config = self.a_config([stand_in_drone], app_config)
        assert isinstance(SquadFlightFactory(config, UUID(str(MISSION_ID))), FlightFactory)

    def test_it_creates_a_squad_flight_whose_drone_service_holds_every_registered_drone(
        self, stand_in_drones: StandInDrones, app_config: partial[Path]
    ) -> None:
        stand_ins = [stand_in_drones.make() for _ in range(SQUAD_SIZE)]
        config = self.a_config(stand_ins, app_config)
        squad = SquadFlightFactory(config, UUID(str(MISSION_ID))).create()
        assert isinstance(squad, SquadFlight)
        assert isinstance(squad.service, DroneService)
        assert [drone.drone_id for drone in squad.service.registry.drones()] == [UUID(DRONE_IDS[0]), UUID(DRONE_IDS[1])]
        assert squad.mission_id == UUID(str(MISSION_ID))
        assert squad.status_interval_s == config.flight.status_interval_s

    async def test_the_created_squad_flies_and_completes(
        self, stand_in_drones: StandInDrones, app_config: partial[Path]
    ) -> None:
        stand_ins = [stand_in_drones.make() for _ in range(SQUAD_SIZE)]
        config = self.a_config(stand_ins, app_config)
        squad = SquadFlightFactory(config, UUID(str(MISSION_ID))).create()
        statuses = [status async for status in squad.execute()]
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert squad.all_completed is True
