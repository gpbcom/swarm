from __future__ import annotations

# Standard library imports
from typing import Callable, List
from uuid import UUID

# Third-party imports
import pytest
from flight_engine_recording_sink import RecordingFrameSink
from flight_engine_stand_in_source import StandInSampleSource

# First-party imports
from flight_engine.models.config.flight_engine_config import FlightEngineConfig
from flight_engine.models.missions.drone_entry import DroneEntry
from flight_engine.models.missions.mission_entry import MissionEntry
from flight_engine.models.telemetry.drone_sample import DroneSample
from flight_engine.models.telemetry.drone_state_catalog import DroneStateCatalog
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub
from swarm_models.models.telemetry.enums.drone_state import DroneState

UUID_TEMPLATE = "01943c5e-8a4b-7c2d-9e1f-{number:012x}"
OPERATOR_NUMBER = 1
MISSION_NUMBER = 100
DRONE_NUMBER = 1000
SYSTEM_STATUS_STANDBY = 3
SYSTEM_STATUS_ACTIVE = 4
FIRST_MAVLINK_PORT = 14550
TICK_INTERVAL_MS = 50
STATUS_INTERVAL_S = 0.05
LINK_LOST_AFTER_MS = 5000


def a_uuid(number: int) -> UUID:
    return UUID(UUID_TEMPLATE.format(number=number))


def make_mission(
    drone_count: int = 3, operator_number: int = OPERATOR_NUMBER, mission_number: int = MISSION_NUMBER
) -> MissionEntry:
    drones: List[DroneEntry] = [
        DroneEntry(system_id=index + 1, drone_id=a_uuid(DRONE_NUMBER + mission_number * 10 + index))
        for index in range(drone_count)
    ]
    return MissionEntry(
        operator_id=a_uuid(operator_number),
        mission_id=a_uuid(mission_number),
        mavlink_port=FIRST_MAVLINK_PORT + mission_number,
        drones=drones,
    )


def make_sample(
    system_id: int = 1,
    has_position: bool = True,
    lat_e7: int = 475000000,
    lon_e7: int = 85000000,
    relative_alt_mm: int = 12000,
    vx_cm_s: int = 0,
    vy_cm_s: int = 0,
    hdg_cdeg: int = 0,
    battery_remaining: int = 80,
    system_status: int = SYSTEM_STATUS_ACTIVE,
    received: int = 10,
    lost: int = 0,
    updated_at_us: int = 1_000_000,
) -> DroneSample:
    return DroneSample(
        system_id=system_id,
        has_position=has_position,
        lat_e7=lat_e7,
        lon_e7=lon_e7,
        relative_alt_mm=relative_alt_mm,
        vx_cm_s=vx_cm_s,
        vy_cm_s=vy_cm_s,
        hdg_cdeg=hdg_cdeg,
        battery_remaining=battery_remaining,
        base_mode=0,
        system_status=system_status,
        received=received,
        lost=lost,
        updated_at_us=updated_at_us,
    )


@pytest.fixture
def mission_factory() -> Callable[..., MissionEntry]:
    return make_mission


@pytest.fixture
def sample_factory() -> Callable[..., DroneSample]:
    return make_sample


@pytest.fixture
def mission() -> MissionEntry:
    return make_mission()


@pytest.fixture
def states() -> DroneStateCatalog:
    return DroneStateCatalog(
        system_status_states={SYSTEM_STATUS_STANDBY: DroneState.READY, SYSTEM_STATUS_ACTIVE: DroneState.AIRBORNE},
        default_state=DroneState.GROUNDED,
    )


@pytest.fixture
def flight_engine_config() -> FlightEngineConfig:
    return FlightEngineConfig(
        tick_interval_ms=TICK_INTERVAL_MS,
        status_interval_s=STATUS_INTERVAL_S,
        link_lost_after_ms=LINK_LOST_AFTER_MS,
    )


@pytest.fixture
def stand_in_source() -> StandInSampleSource:
    return StandInSampleSource()


@pytest.fixture
def recording_sink() -> RecordingFrameSink:
    return RecordingFrameSink()


@pytest.fixture
def hub() -> LiveHub:
    return LiveHub()


@pytest.fixture
def codec() -> LiveCodec:
    return LiveCodec()
