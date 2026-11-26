from __future__ import annotations

# Standard library imports
import asyncio
import logging
from contextlib import suppress
from typing import Callable, ClassVar, List

# Third-party imports
import pytest
from flight_engine_recording_sink import RecordingFrameSink
from flight_engine_stand_in_source import StandInSampleSource

# First-party imports
from flight_engine.models.config.flight_engine_config import FlightEngineConfig
from flight_engine.models.missions.mission_entry import MissionEntry
from flight_engine.models.telemetry.drone_sample import DroneSample
from flight_engine.models.telemetry.drone_state_catalog import DroneStateCatalog
from flight_engine.service.missions.mission_actor import MissionActor
from flight_engine.service.missions.squad_frame_builder import SquadFrameBuilder
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub
from swarm_models.models.enums import LiveTopicKind
from swarm_models.models.live.live_subscription import LiveSubscription


class TestMissionActor:
    RUN_S: ClassVar[float] = 0.5
    MIN_TICKS: ClassVar[int] = 6
    MAX_TICKS: ClassVar[int] = 12
    SLOW_SINK_S: ClassVar[float] = 0.2
    TEN_DRONES: ClassVar[int] = 10

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
