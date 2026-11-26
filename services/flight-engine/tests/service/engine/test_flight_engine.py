from __future__ import annotations

# Standard library imports
import asyncio
from contextlib import suppress
from typing import Callable, ClassVar, Dict, List, Tuple
from uuid import UUID

# Third-party imports
from flight_engine_stand_in_source import StandInSampleSource  # isort: skip
from nats.aio.client import Client

# First-party imports
from flight_engine.models.config.flight_engine_config import FlightEngineConfig
from flight_engine.models.missions.mission_catalog import MissionCatalog
from flight_engine.models.missions.mission_entry import MissionEntry
from flight_engine.models.telemetry.drone_sample import DroneSample
from flight_engine.models.telemetry.drone_state_catalog import DroneStateCatalog
from flight_engine.service.engine.flight_engine import FlightEngine
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_live.service.live_codec import LiveCodec
from swarm_live.service.live_hub import LiveHub
from swarm_models.enums import LiveTopicKind
from swarm_models.subjects.operator_subjects import OperatorSubjects
from swarm_nats.clients.nats_connector import NatsConnector
from swarm_nats.models.config.nats_client_config import NatsClientConfig


class TestFlightEngine:
    FIRST_OPERATOR: ClassVar[int] = 1
    SECOND_OPERATOR: ClassVar[int] = 2
    FIRST_MISSION: ClassVar[int] = 100
    SECOND_MISSION: ClassVar[int] = 101
    FIRST_DRONES: ClassVar[int] = 2
    SECOND_DRONES: ClassVar[int] = 3
    MESSAGE_TIMEOUT_S: ClassVar[float] = 5.0
    STATUS_POLL_S: ClassVar[float] = 0.01

    def engine(
        self,
        config: FlightEngineConfig,
        missions: MissionCatalog,
        states: DroneStateCatalog,
        sources: Dict[UUID, StandInSampleSource],
    ) -> FlightEngine:
        connector = NatsConnector(config.nats)
        return FlightEngine(
            config, missions, states, LiveHub(), LiveCodec(), lambda entry: sources[entry.mission_id], connector
        )

    def config(self, nats_url: str, base: FlightEngineConfig) -> FlightEngineConfig:
        return FlightEngineConfig(
            tick_interval_ms=base.tick_interval_ms,
            status_interval_s=base.status_interval_s,
            link_lost_after_ms=base.link_lost_after_ms,
            nats=NatsClientConfig(servers=[nats_url]),
        )

    def two_missions(
        self,
        mission_factory: Callable[..., MissionEntry],
        sample_factory: Callable[..., DroneSample],
    ) -> Tuple[MissionCatalog, Dict[UUID, StandInSampleSource]]:
        first = mission_factory(self.FIRST_DRONES, self.FIRST_OPERATOR, self.FIRST_MISSION)
        second = mission_factory(self.SECOND_DRONES, self.SECOND_OPERATOR, self.SECOND_MISSION)
        first_samples = [sample_factory(system_id=index + 1) for index in range(self.FIRST_DRONES)]
        second_samples = [sample_factory(system_id=index + 1) for index in range(self.SECOND_DRONES)]
        sources = {
            first.mission_id: StandInSampleSource(first_samples),
            second.mission_id: StandInSampleSource(second_samples),
        }
        return MissionCatalog(missions=[first, second]), sources

    async def read_statuses(self, engine: FlightEngine, statuses: List[RunnableStatus]) -> None:
        async for status in engine.execute():
            statuses.append(status)

    async def test_an_engine_with_two_missions_has_two_actors(
        self,
        nats_url: str,
        flight_engine_config: FlightEngineConfig,
        states: DroneStateCatalog,
        mission_factory: Callable[..., MissionEntry],
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        missions, sources = self.two_missions(mission_factory, sample_factory)
        engine = self.engine(self.config(nats_url, flight_engine_config), missions, states, sources)
        try:
            await engine.initialize()
            assert len(engine.actors) == 2
        finally:
            await engine.close()

    async def test_frames_of_each_mission_arrive_on_its_nats_subject(
        self,
        nats_url: str,
        nats_client: Client,
        flight_engine_config: FlightEngineConfig,
        states: DroneStateCatalog,
        mission_factory: Callable[..., MissionEntry],
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        missions, sources = self.two_missions(mission_factory, sample_factory)
        first, second = missions.missions
        codec = LiveCodec()
        first_subject = OperatorSubjects(operator_id=first.operator_id).mission(first.mission_id, LiveTopicKind.SQUAD)
        second_subject = OperatorSubjects(operator_id=second.operator_id).mission(
            second.mission_id, LiveTopicKind.SQUAD
        )
        first_subscription = await nats_client.subscribe(first_subject)
        second_subscription = await nats_client.subscribe(second_subject)
        await nats_client.flush()
        engine = self.engine(self.config(nats_url, flight_engine_config), missions, states, sources)
        statuses: List[RunnableStatus] = []
        task = asyncio.create_task(self.read_statuses(engine, statuses))
        try:
            first_message = await first_subscription.next_msg(timeout=self.MESSAGE_TIMEOUT_S)
            second_message = await second_subscription.next_msg(timeout=self.MESSAGE_TIMEOUT_S)
            deadline = asyncio.get_running_loop().time() + self.MESSAGE_TIMEOUT_S
            while not statuses and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(self.STATUS_POLL_S)
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        first_squad = codec.decode_squad_frame(first_message.data)
        second_squad = codec.decode_squad_frame(second_message.data)
        assert first_squad.mission_id == first.mission_id
        assert len(first_squad.frames) == self.FIRST_DRONES
        assert second_squad.mission_id == second.mission_id
        assert len(second_squad.frames) == self.SECOND_DRONES
        assert statuses
        assert all(isinstance(status, RunnableStatus) for status in statuses)

    async def test_close_closes_every_source(
        self,
        nats_url: str,
        flight_engine_config: FlightEngineConfig,
        states: DroneStateCatalog,
        mission_factory: Callable[..., MissionEntry],
        sample_factory: Callable[..., DroneSample],
    ) -> None:
        missions, sources = self.two_missions(mission_factory, sample_factory)
        engine = self.engine(self.config(nats_url, flight_engine_config), missions, states, sources)
        await engine.initialize()
        await engine.close()
        assert all(source.closed for source in sources.values())
