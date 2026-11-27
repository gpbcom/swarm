from __future__ import annotations

# Standard library imports
from typing import Callable, ClassVar, List
from uuid import UUID

# Third-party imports
import pytest
from opentelemetry import trace

# First-party imports
from swarm_models.flight.missions.mission_entry import MissionEntry
from swarm_models.flight.telemetry.drone_sample import DroneSample
from swarm_models.flight.telemetry.drone_state_catalog import DroneStateCatalog
from swarm_models.telemetry.enums.drone_state import DroneState
from swarm_models.telemetry.squad_frame import SquadFrame
from swarm_models.telemetry.telemetry_frame import TelemetryFrame
from swarm_service.flight.missions.squad_frame_builder import SquadFrameBuilder
from tests.fakes.signals.recorded_signals import RecordedSignals


class TestSquadFrameBuilder:
    LINK_LOST_AFTER_MS: ClassVar[int] = 5000
    NOW_US: ClassVar[int] = 2_000_000
    TEN_DRONES: ClassVar[int] = 10
    UNKNOWN_SYSTEM_ID: ClassVar[int] = 200
    TRACEPARENT_TEMPLATE: ClassVar[str] = "00-{trace_id:032x}-{span_id:016x}-{flags:02x}"
    SPAN_NAME: ClassVar[str] = "test.span"

    def builder(self, mission: MissionEntry, states: DroneStateCatalog) -> SquadFrameBuilder:
        return SquadFrameBuilder(mission, states, self.LINK_LOST_AFTER_MS)

    def frame_of(self, squad: SquadFrame, drone_id: UUID) -> TelemetryFrame:
        matching = [frame for frame in squad.frames if frame.drone_id == drone_id]
        assert len(matching) == 1
        return matching[0]

    def first_frame(
        self, mission: MissionEntry, states: DroneStateCatalog, sample: DroneSample, now_us: int
    ) -> TelemetryFrame:
        squad = self.builder(mission, states).build([sample], now_us)
        return self.frame_of(squad, mission.drones[0].drone_id)

    def test_the_squad_frame_belongs_to_the_mission_and_the_tick(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        squad = self.builder(mission, states).build([sample_factory(system_id=1)], self.NOW_US)
        assert squad.mission_id == mission.mission_id
        assert squad.t_us == self.NOW_US

    def test_ten_drones_give_one_squad_frame_of_ten_frames(
        self,
        mission_factory: Callable[..., MissionEntry],
        states: DroneStateCatalog,
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        mission = mission_factory(self.TEN_DRONES)
        samples = [sample_factory(system_id=index + 1) for index in range(self.TEN_DRONES)]
        squad = self.builder(mission, states).build(samples, self.NOW_US)
        assert len(squad.frames) == self.TEN_DRONES
        assert {frame.drone_id for frame in squad.frames} == {drone.drone_id for drone in mission.drones}

    def test_a_sample_of_a_system_id_outside_the_mission_is_ignored(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        samples = [sample_factory(system_id=1), sample_factory(system_id=self.UNKNOWN_SYSTEM_ID)]
        squad = self.builder(mission, states).build(samples, self.NOW_US)
        assert [frame.drone_id for frame in squad.frames] == [mission.drones[0].drone_id]

    def test_a_drone_without_a_known_position_does_not_appear(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        samples = [sample_factory(system_id=1, has_position=False), sample_factory(system_id=2)]
        squad = self.builder(mission, states).build(samples, self.NOW_US)
        assert [frame.drone_id for frame in squad.frames] == [mission.drones[1].drone_id]

    def test_no_sample_gives_an_empty_squad_frame(self, mission: MissionEntry, states: DroneStateCatalog) -> None:
        assert self.builder(mission, states).build([], self.NOW_US).frames == []

    def test_the_position_is_copied(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        sample = sample_factory(system_id=1, lat_e7=-338000000, lon_e7=1512000000)
        frame = self.first_frame(mission, states, sample, self.NOW_US)
        assert frame.lat_e7 == sample.lat_e7
        assert frame.lon_e7 == sample.lon_e7

    def test_the_altitude_is_in_metres(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        sample = sample_factory(system_id=1, relative_alt_mm=12345)
        assert self.first_frame(mission, states, sample, self.NOW_US).altitude_m == pytest.approx(12.345)

    def test_the_speed_is_the_ground_speed_in_metres_per_second(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        sample = sample_factory(system_id=1, vx_cm_s=300, vy_cm_s=-400)
        assert self.first_frame(mission, states, sample, self.NOW_US).speed_m_s == pytest.approx(5.0)

    @pytest.mark.parametrize(
        ("hdg_cdeg", "heading_deg"),
        [(9000, 90.0), (0, 0.0), (35999, 359.99), (65535, 0.0)],
    )
    def test_the_heading_is_in_degrees_and_zero_when_unknown(
        self,
        mission: MissionEntry,
        states: DroneStateCatalog,
        sample_factory: Callable[..., DroneSample],
        hdg_cdeg: int,
        heading_deg: float,
    ) -> None:
        sample = sample_factory(system_id=1, hdg_cdeg=hdg_cdeg)
        assert self.first_frame(mission, states, sample, self.NOW_US).heading_deg == pytest.approx(heading_deg)

    @pytest.mark.parametrize(("battery_remaining", "battery_pct"), [(80, 80.0), (0, 0.0), (100, 100.0), (-1, 0.0)])
    def test_the_battery_is_zero_when_unknown(
        self,
        mission: MissionEntry,
        states: DroneStateCatalog,
        sample_factory: Callable[..., DroneSample],
        battery_remaining: int,
        battery_pct: float,
    ) -> None:
        sample = sample_factory(system_id=1, battery_remaining=battery_remaining)
        assert self.first_frame(mission, states, sample, self.NOW_US).battery_pct == pytest.approx(battery_pct)

    @pytest.mark.parametrize(
        ("received", "lost", "link_quality_pct"),
        [(3, 1, 75.0), (10, 0, 100.0), (0, 0, 100.0), (1, 3, 25.0)],
    )
    def test_the_link_quality_is_the_share_of_received_frames(
        self,
        mission: MissionEntry,
        states: DroneStateCatalog,
        sample_factory: Callable[..., DroneSample],
        received: int,
        lost: int,
        link_quality_pct: float,
    ) -> None:
        sample = sample_factory(system_id=1, received=received, lost=lost)
        frame = self.first_frame(mission, states, sample, self.NOW_US)
        assert frame.link_quality_pct == pytest.approx(link_quality_pct)

    def test_the_state_comes_from_the_state_catalog(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        sample = sample_factory(system_id=1, system_status=4)
        frame = self.first_frame(mission, states, sample, self.NOW_US)
        assert frame.state == states.state_of(sample.system_status)
        assert frame.state == DroneState.AIRBORNE

    def test_a_drone_silent_for_longer_than_the_limit_is_lost(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        sample = sample_factory(system_id=1, updated_at_us=0)
        frame = self.first_frame(mission, states, sample, self.LINK_LOST_AFTER_MS * 1000 + 1)
        assert frame.state == DroneState.LOST

    def test_a_drone_silent_for_exactly_the_limit_is_not_lost(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        sample = sample_factory(system_id=1, updated_at_us=0)
        frame = self.first_frame(mission, states, sample, self.LINK_LOST_AFTER_MS * 1000)
        assert frame.state == DroneState.AIRBORNE

    def test_the_frame_time_is_the_time_of_the_sample(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        sample = sample_factory(system_id=1, updated_at_us=1_234_567)
        assert self.first_frame(mission, states, sample, self.NOW_US).t_us == sample.updated_at_us

    def test_the_sequence_counts_from_zero_and_goes_up_at_each_build(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        builder = self.builder(mission, states)
        samples = [sample_factory(system_id=1)]
        drone_id = mission.drones[0].drone_id
        sequences: List[int] = [self.frame_of(builder.build(samples, self.NOW_US), drone_id).seq for _ in range(3)]
        assert sequences == [0, 1, 2]

    def test_each_drone_has_its_own_sequence(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        builder = self.builder(mission, states)
        first, second = mission.drones[0].drone_id, mission.drones[1].drone_id
        builder.build([sample_factory(system_id=1)], self.NOW_US)
        squad = builder.build([sample_factory(system_id=1), sample_factory(system_id=2)], self.NOW_US)
        assert self.frame_of(squad, first).seq == 1
        assert self.frame_of(squad, second).seq == 0

    def test_inside_a_span_the_squad_frame_carries_its_traceparent(
        self,
        mission: MissionEntry,
        states: DroneStateCatalog,
        sample_factory: Callable[..., DroneSample],
        recorded_signals: RecordedSignals,
    ) -> None:
        with trace.get_tracer(__name__).start_as_current_span(self.SPAN_NAME) as span:
            squad = self.builder(mission, states).build([sample_factory(system_id=1)], self.NOW_US)
            context = span.get_span_context()
        expected = self.TRACEPARENT_TEMPLATE.format(
            trace_id=context.trace_id, span_id=context.span_id, flags=int(context.trace_flags)
        )
        assert squad.trace_parent == expected

    def test_outside_any_span_the_squad_frame_has_no_traceparent(
        self, mission: MissionEntry, states: DroneStateCatalog, sample_factory: Callable[..., DroneSample]
    ) -> None:
        squad = self.builder(mission, states).build([sample_factory(system_id=1)], self.NOW_US)
        assert squad.trace_parent is None
