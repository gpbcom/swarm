from __future__ import annotations

# Standard library imports
from pathlib import Path
from typing import List, Optional
from uuid import UUID

# First-party imports
from swarm_models.config.simulator.flight_config import FlightConfig
from swarm_models.enums import SimulatedDroneKind
from swarm_models.simulation.registry.registered_drone import RegisteredDrone
from swarm_models.simulation.routes.route import Route
from swarm_models.simulation.routes.waypoint import Waypoint
from tests.fakes.mavlink.stand_in_drone import StandInDrone

OPERATOR_ID = "01934f5e-0000-7000-8000-0000000000a1"
MISSION_ID = "01934f5e-0000-7000-8000-0000000000b1"
DRONE_IDS: List[str] = [f"01934f5e-0000-7000-8000-0000000000{index:02x}" for index in range(1, 12)]
START_LAT_E7 = 473977420
START_LON_E7 = 85455940
SQUARE_STEP_E7 = 4500
SQUARE_ALTITUDE_M = 20.0
HEARTBEAT_TIMEOUT_S = 2.0
ARM_TIMEOUT_S = 2.0
ROUTE_TIMEOUT_S = 5.0
STATUS_INTERVAL_S = 0.1


def a_registered_drone(
    stand_in: StandInDrone, index: int = 0, kind: SimulatedDroneKind = SimulatedDroneKind.SYNTHETIC
) -> RegisteredDrone:
    return RegisteredDrone(
        drone_id=UUID(DRONE_IDS[index]),
        kind=kind,
        host=stand_in.host,
        port=stand_in.port,
        system_id=stand_in.system_id,
    )


def a_flight_config() -> FlightConfig:
    return FlightConfig(
        heartbeat_timeout_s=HEARTBEAT_TIMEOUT_S,
        arm_timeout_s=ARM_TIMEOUT_S,
        route_timeout_s=ROUTE_TIMEOUT_S,
        status_interval_s=STATUS_INTERVAL_S,
    )


def a_square_route() -> Route:
    corners = [
        (0, 0),
        (SQUARE_STEP_E7, 0),
        (SQUARE_STEP_E7, SQUARE_STEP_E7),
        (0, SQUARE_STEP_E7),
        (0, 0),
    ]
    return Route(
        waypoints=[
            Waypoint(
                lat_e7=START_LAT_E7 + north_e7,
                lon_e7=START_LON_E7 + east_e7,
                altitude_m=SQUARE_ALTITUDE_M,
            )
            for north_e7, east_e7 in corners
        ]
    )


APP_NAME = "app.yaml"
SQUAD_NAME = "simulated_squad.yaml"
MAPPING_NAME = "command_mapping.yaml"
FLIGHT_LOG_NAME = "flight_log.sqlite3"
UNUSED_CREDS_NAME = "unused.creds"
UNUSED_SERVER = "nats://127.0.0.1:4222"
ENCODING = "utf-8"
QUEUE_GROUP = "simulator"
SQUAD_HEAD = "drones:\n"
DRONE_ENTRY = (
    "  - drone_id: {drone_id}\n    kind: {kind}\n    host: {host}\n    port: {port}\n    system_id: {system_id}\n"
)
MAPPING_TEXT = "commands:\n  hold:\n    command_id: 193\n    param1: 0.0\n  return_home:\n    command_id: 20\n"
APP_TEMPLATE = """operator_id: {operator_id}
nats:
  servers: ["{server}"]
  credentials_path: {creds}
  connect_timeout_s: 5.0
responder:
  subject: op.{operator_id}.mission.*.command
  queue_group: {queue_group}
  idempotency_bucket: idempotency
  idempotency_ttl_s: 600.0
  replicas: 1
  status_interval_s: 0.2
registry:
  squad_catalog_path: {squad}
  command_mapping_path: {mapping}
flight:
  heartbeat_timeout_s: 2.0
  arm_timeout_s: 2.0
  route_timeout_s: 2.0
  status_interval_s: 0.1
flight_log_path: {flight_log}
"""


def write_app_config(
    directory: Path,
    drones: List[RegisteredDrone],
    server: str = UNUSED_SERVER,
    creds: Optional[Path] = None,
) -> Path:
    """Write the app.yaml of the Simulator and the catalogs of stand-in Drones it points at, to a folder."""
    directory.mkdir(parents=True, exist_ok=True)
    squad = directory / SQUAD_NAME
    mapping = directory / MAPPING_NAME
    entries = "".join(
        DRONE_ENTRY.format(
            drone_id=drone.drone_id,
            kind=drone.kind,
            host=drone.host,
            port=drone.port,
            system_id=drone.system_id,
        )
        for drone in drones
    )
    squad.write_text(SQUAD_HEAD + entries, encoding=ENCODING)
    mapping.write_text(MAPPING_TEXT, encoding=ENCODING)
    if creds is None:
        creds = directory / UNUSED_CREDS_NAME
    path = directory / APP_NAME
    path.write_text(
        APP_TEMPLATE.format(
            operator_id=OPERATOR_ID,
            server=server,
            creds=creds,
            queue_group=QUEUE_GROUP,
            squad=squad,
            mapping=mapping,
            flight_log=directory / FLIGHT_LOG_NAME,
        ),
        encoding=ENCODING,
    )
    return path
