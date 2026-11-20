from __future__ import annotations

from pathlib import Path
from typing import List
from uuid import UUID

from services.simulator.tests.helpers import DRONE_IDS, MISSION_ID, OPERATOR_ID
from services.simulator.tests.stand_in_drone import StandInDrone
from services.simulator.tests.stand_in_drones import StandInDrones
from simulator.models.config.simulator_config import SimulatorConfig
from simulator.models.enums import SimulatedDroneKind
from simulator.service.factories.flight_factory import FlightFactory
from simulator.service.factories.flights.squad_flight_factory import SquadFlightFactory
from simulator.service.flights.squad_flight import SquadFlight
from swarm_lifecycle.models.enums import RunnableStatus

CATALOG_FILE = "simulated_squad.yaml"
CONFIG_FILE = "app.yaml"
CREDENTIALS_FILE = "simulated.creds"
FLIGHT_LOG_FILE = "flight_log.sqlite3"
SQUAD_SIZE = 2


class TestSquadFlightFactory:
    def a_config(self, stand_ins: List[StandInDrone], tmp_path: Path) -> SimulatorConfig:
        drones = "".join(
            f"  - drone_id: '{DRONE_IDS[index]}'\n"
            f"    kind: {SimulatedDroneKind.SYNTHETIC.value}\n"
            f"    host: {stand_in.host}\n"
            f"    port: {stand_in.port}\n"
            f"    system_id: {stand_in.system_id}\n"
            for index, stand_in in enumerate(stand_ins)
        )
        catalog_path = tmp_path / CATALOG_FILE
        catalog_path.write_text(f"drones:\n{drones}", encoding="utf-8")
        config_path = tmp_path / CONFIG_FILE
        config_path.write_text(
            f"operator_id: '{OPERATOR_ID}'\n"
            f"nats:\n  credentials_path: {tmp_path / CREDENTIALS_FILE}\n"
            f"responder:\n  subject: op.{OPERATOR_ID}.mission.*.command\n  queue_group: simulator\n"
            f"registry:\n  squad_catalog_path: {catalog_path}\n"
            f"flight:\n  heartbeat_timeout_s: 1.0\n  arm_timeout_s: 2.0\n  route_timeout_s: 2.0\n"
            f"  status_interval_s: 0.1\n"
            f"flight_log_path: {tmp_path / FLIGHT_LOG_FILE}\n",
            encoding="utf-8",
        )
        return SimulatorConfig.load(config_path)

    def test_it_is_a_flight_factory(self, stand_in_drone: StandInDrone, tmp_path: Path) -> None:
        config = self.a_config([stand_in_drone], tmp_path)
        assert isinstance(SquadFlightFactory(config, UUID(str(MISSION_ID))), FlightFactory)

    def test_it_creates_one_drone_flight_per_registered_drone(
        self, stand_in_drones: StandInDrones, tmp_path: Path
    ) -> None:
        stand_ins = [stand_in_drones.make() for _ in range(SQUAD_SIZE)]
        config = self.a_config(stand_ins, tmp_path)
        squad = SquadFlightFactory(config, UUID(str(MISSION_ID))).create()
        assert isinstance(squad, SquadFlight)
        assert [flight.drone.drone_id for flight in squad.flights] == [UUID(DRONE_IDS[0]), UUID(DRONE_IDS[1])]
        assert all(flight.store is squad.store for flight in squad.flights)
        assert squad.status_interval_s == config.flight.status_interval_s

    async def test_the_created_squad_flies_and_completes(self, stand_in_drones: StandInDrones, tmp_path: Path) -> None:
        stand_ins = [stand_in_drones.make() for _ in range(SQUAD_SIZE)]
        config = self.a_config(stand_ins, tmp_path)
        squad = SquadFlightFactory(config, UUID(str(MISSION_ID))).create()
        statuses = [status async for status in squad.execute()]
        assert statuses[-1] == RunnableStatus.EXECUTED
        assert squad.all_completed is True
