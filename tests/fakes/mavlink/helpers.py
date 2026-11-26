from __future__ import annotations

# Standard library imports
from typing import List
from uuid import UUID

# First-party imports
from services.simulator.tests.stand_in_drone import StandInDrone
from simulator.models.config.flight_config import FlightConfig
from simulator.models.enums import SimulatedDroneKind
from simulator.models.registry.registered_drone import RegisteredDrone
from simulator.models.routes.route import Route
from simulator.models.routes.waypoint import Waypoint

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
