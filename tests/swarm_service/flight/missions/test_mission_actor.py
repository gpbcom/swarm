from __future__ import annotations

# Standard library imports
import asyncio
import logging
from contextlib import suppress
from typing import Callable, ClassVar, List, Optional, Set, Tuple
from uuid import UUID

# Third-party imports
import pytest
from opentelemetry import baggage, trace
from opentelemetry.sdk.trace import ReadableSpan

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.enums import LiveTopicKind
from swarm_models.flight.missions.mission_entry import MissionEntry
from swarm_models.flight.telemetry.drone_sample import DroneSample
from swarm_models.flight.telemetry.drone_state_catalog import DroneStateCatalog
from swarm_models.live.live_subscription import LiveSubscription
from swarm_service.flight.missions.mission_actor import MissionActor
from swarm_service.flight.missions.squad_frame_builder import SquadFrameBuilder
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.live_codec import LiveCodec
from tests.fakes.signals.recorded_signals import RecordedSignals
from tests.swarm_service.flight.flight_engine_recording_sink import RecordingFrameSink
from tests.swarm_service.flight.flight_engine_stand_in_source import StandInSampleSource


class TestMissionActor:
    RUN_S: ClassVar[float] = 0.5
    MIN_TICKS: ClassVar[int] = 6
    MAX_TICKS: ClassVar[int] = 12
    SLOW_SINK_S: ClassVar[float] = 0.2
    TEN_DRONES: ClassVar[int] = 10
    OPERATOR_KEY: ClassVar[str] = "operator_id"
    MISSION_KEY: ClassVar[str] = "mission_id"
    FORBIDDEN_KEYS: ClassVar[Set[str]] = {"drone_id", "latitude", "longitude", "lat", "lon", "lat_e7", "lon_e7"}

    def setup_method(self) -> None:
        self.contexts: List[Tuple[Optional[str], Optional[str], int]] = []

    def actor(
        self,
        config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        source: StandInSampleSource,
        sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
    ) -> MissionActor:
        builder = SquadFrameBuilder(mission, states, config.link_lost_after_ms)
        return MissionActor(config, mission, source, builder, sink, hub, codec)

    async def read_statuses(self, actor: MissionActor, statuses: List[RunnableStatus]) -> None:
        async for status in actor.execute():
            statuses.append(status)

    async def run_for(self, actor: MissionActor, duration_s: float) -> List[RunnableStatus]:
        statuses: List[RunnableStatus] = []
        task = asyncio.create_task(self.read_statuses(actor, statuses))
        await asyncio.sleep(duration_s)
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        return statuses

    async def test_an_actor_emits_about_one_frame_per_tick(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        stand_in_source.samples = [sample_factory(system_id=1)]
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, recording_sink, hub, codec)
        await self.run_for(actor, self.RUN_S)
        assert self.MIN_TICKS <= actor.ticks <= self.MAX_TICKS
        assert len(recording_sink.published) == actor.ticks

    async def test_the_sink_gets_the_operator_the_mission_and_the_encoded_frame(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        stand_in_source.samples = [sample_factory(system_id=1)]
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, recording_sink, hub, codec)
        await self.run_for(actor, self.RUN_S)
        operator_id, mission_id, data = recording_sink.published[0]
        assert operator_id == mission.operator_id
        assert mission_id == mission.mission_id
        squad = codec.decode_squad_frame(data)
        assert squad.mission_id == mission.mission_id
        assert len(squad.frames) == 1

    async def test_the_hub_mailbox_gets_the_encoded_frame(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        stand_in_source.samples = [sample_factory(system_id=1), sample_factory(system_id=2)]
        topic = LiveSubscription.topic_of(mission.mission_id, LiveTopicKind.SQUAD)
        mailbox, first = hub.subscribe(topic)
        assert first
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, recording_sink, hub, codec)
        await self.run_for(actor, self.RUN_S)
        assert mailbox.pending()
        squad = codec.decode_squad_frame(await mailbox.take())
        assert squad.mission_id == mission.mission_id
        assert len(squad.frames) == 2

    async def test_ten_drones_give_one_squad_frame_of_ten_frames(
        self,
        flight_engine_config: FlightEngineConfig,
        mission_factory: Callable[..., MissionEntry],
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        mission = mission_factory(self.TEN_DRONES)
        stand_in_source.samples = [sample_factory(system_id=index + 1) for index in range(self.TEN_DRONES)]
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, recording_sink, hub, codec)
        await self.run_for(actor, self.RUN_S)
        squad = codec.decode_squad_frame(recording_sink.published[0][2])
        assert len(squad.frames) == self.TEN_DRONES

    async def test_a_failing_sink_does_not_stop_the_ticks(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        sink = RecordingFrameSink(failing=True)
        stand_in_source.samples = [sample_factory(system_id=1)]
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, sink, hub, codec)
        with caplog.at_level(logging.WARNING):
            await self.run_for(actor, self.RUN_S)
        assert actor.ticks >= self.MIN_TICKS
        assert sink.attempts >= self.MIN_TICKS
        assert any(record.levelno == logging.WARNING for record in caplog.records)

    async def test_a_slow_sink_does_not_stop_the_ticks(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        sink = RecordingFrameSink(delay_s=self.SLOW_SINK_S)
        stand_in_source.samples = [sample_factory(system_id=1)]
        topic = LiveSubscription.topic_of(mission.mission_id, LiveTopicKind.SQUAD)
        mailbox, _ = hub.subscribe(topic)
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, sink, hub, codec)
        await self.run_for(actor, self.RUN_S)
        assert actor.ticks >= 2
        assert mailbox.pending()

    async def test_execute_yields_runnable_statuses(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        stand_in_source.samples = [sample_factory(system_id=1)]
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, recording_sink, hub, codec)
        statuses = await self.run_for(actor, self.RUN_S)
        assert statuses
        assert all(isinstance(status, RunnableStatus) for status in statuses)
        assert RunnableStatus.RUNNING in statuses

    async def test_close_closes_the_source(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
    ) -> None:
        actor = self.actor(flight_engine_config, mission, states, stand_in_source, recording_sink, hub, codec)
        await self.run_for(actor, self.RUN_S)
        assert stand_in_source.closed

    async def capture_publish(self, sink: RecordingFrameSink, operator_id: UUID, mission_id: UUID, data: bytes) -> None:
        operator = baggage.get_baggage(self.OPERATOR_KEY)
        mission = baggage.get_baggage(self.MISSION_KEY)
        self.contexts.append(
            (
                None if operator is None else str(operator),
                None if mission is None else str(mission),
                trace.get_current_span().get_span_context().span_id,
            )
        )
        await RecordingFrameSink.publish(sink, operator_id, mission_id, data)

    def root_spans(self, recorded_signals: RecordedSignals) -> List[ReadableSpan]:
        return [span for span in recorded_signals.spans() if span.parent is None]

    async def traced_run(
        self,
        config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        source: StandInSampleSource,
        sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample: DroneSample,
    ) -> MissionActor:
        source.samples = [sample]
        actor = self.actor(config, mission, states, source, sink, hub, codec)
        await self.run_for(actor, self.RUN_S)
        return actor

    async def test_each_tick_produces_one_root_span_with_the_operator_and_the_mission(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
        recorded_signals: RecordedSignals,
    ) -> None:
        actor = await self.traced_run(
            flight_engine_config,
            mission,
            states,
            stand_in_source,
            recording_sink,
            hub,
            codec,
            sample_factory(system_id=1),
        )
        roots = self.root_spans(recorded_signals)
        assert len(roots) == actor.ticks
        for span in roots:
            assert span.attributes is not None
            assert span.attributes[self.OPERATOR_KEY] == str(mission.operator_id)
            assert span.attributes[self.MISSION_KEY] == str(mission.mission_id)

    async def test_the_sink_is_called_inside_the_tick_span_with_the_baggage_of_the_mission(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
        recorded_signals: RecordedSignals,
    ) -> None:
        recording_sink.publish = lambda *args: self.capture_publish(recording_sink, *args)
        await self.traced_run(
            flight_engine_config,
            mission,
            states,
            stand_in_source,
            recording_sink,
            hub,
            codec,
            sample_factory(system_id=1),
        )
        root_ids = {span.context.span_id for span in self.root_spans(recorded_signals)}
        assert self.contexts
        for operator, mission_id, span_id in self.contexts:
            assert operator == str(mission.operator_id)
            assert mission_id == str(mission.mission_id)
            assert span_id in root_ids

    async def test_no_span_or_metric_attribute_is_a_drone_or_a_position(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
        recorded_signals: RecordedSignals,
    ) -> None:
        await self.traced_run(
            flight_engine_config,
            mission,
            states,
            stand_in_source,
            recording_sink,
            hub,
            codec,
            sample_factory(system_id=1),
        )
        keys: Set[str] = set()
        for span in recorded_signals.spans():
            keys |= set(span.attributes or {})
        for name in (MissionActor.FRAMES_METRIC, MissionActor.TICK_DURATION_METRIC):
            for point in recorded_signals.metric_points(name):
                keys |= set(point.attributes)
        assert keys
        assert keys.isdisjoint(self.FORBIDDEN_KEYS)

    async def test_the_tick_metrics_carry_the_operator_and_the_mission_only(
        self,
        flight_engine_config: FlightEngineConfig,
        mission: MissionEntry,
        states: DroneStateCatalog,
        stand_in_source: StandInSampleSource,
        recording_sink: RecordingFrameSink,
        hub: LiveHub,
        codec: LiveCodec,
        sample_factory: Callable[..., DroneSample],
        recorded_signals: RecordedSignals,
    ) -> None:
        actor = await self.traced_run(
            flight_engine_config,
            mission,
            states,
            stand_in_source,
            recording_sink,
            hub,
            codec,
            sample_factory(system_id=1),
        )
        frames = recorded_signals.metric_points(MissionActor.FRAMES_METRIC)
        durations = recorded_signals.metric_points(MissionActor.TICK_DURATION_METRIC)
        assert sum(point.value for point in frames) == actor.ticks
        assert sum(point.count for point in durations) == actor.ticks
        expected = {self.OPERATOR_KEY: str(mission.operator_id), self.MISSION_KEY: str(mission.mission_id)}
        for point in [*frames, *durations]:
            assert dict(point.attributes) == expected
