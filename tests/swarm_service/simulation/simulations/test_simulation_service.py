from __future__ import annotations

# Standard library imports
import asyncio
import logging
from functools import partial
from pathlib import Path
from typing import ClassVar
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.simulation.simulations.exceptions import SESimulationRunningError
from swarm_models.simulation.simulations.simulation_request import SimulationRequest
from swarm_service.simulation.factories.simulations.simulation_service_factory import SimulationServiceFactory
from swarm_service.simulation.simulations.simulation_service import SimulationService
from tests.fakes.mavlink.helpers import DRONE_IDS, MISSION_ID, a_registered_drone
from tests.fakes.mavlink.stand_in_drones import StandInDrones


class TestSimulationService:
    STALL_AFTER_SEQ: ClassVar[int] = 2
    FLIGHT_TIMEOUT_S: ClassVar[float] = 30.0

    def a_service(self, config_path: Path) -> SimulationService:
        return SimulationServiceFactory(SimulatorConfig.load(config_path)).create()

    def a_request(self) -> SimulationRequest:
        return SimulationRequest(mission_id=UUID(str(MISSION_ID)))

    async def wait_for_the_end(self, service: SimulationService) -> None:
        assert service.task is not None
        await asyncio.wait_for(asyncio.shield(service.task), timeout=self.FLIGHT_TIMEOUT_S)

    async def test_two_drones_fly_in_the_background_and_every_route_is_completed(
        self, stand_in_drones: StandInDrones, app_config: partial[Path], caplog: pytest.LogCaptureFixture
    ) -> None:
        stand_ins = [stand_in_drones.make(), stand_in_drones.make()]
        service = self.a_service(app_config([a_registered_drone(s, i) for i, s in enumerate(stand_ins)]))

        with caplog.at_level(logging.INFO):
            accepted = await service.launch(self.a_request())
            await self.wait_for_the_end(service)

        assert accepted.mission_id == UUID(str(MISSION_ID))
        assert accepted.drone_ids == [UUID(DRONE_IDS[0]), UUID(DRONE_IDS[1])]
        assert service.flight is not None
        assert service.flight.all_completed is True
        assert service.flying is False
        assert any("Every Drone completed" in record.getMessage() for record in caplog.records)

    async def test_a_stalled_drone_leaves_the_flight_incomplete_and_is_logged(
        self, stand_in_drones: StandInDrones, app_config: partial[Path], caplog: pytest.LogCaptureFixture
    ) -> None:
        stand_ins = [stand_in_drones.make(), stand_in_drones.make(stall_after_seq=self.STALL_AFTER_SEQ)]
        service = self.a_service(app_config([a_registered_drone(s, i) for i, s in enumerate(stand_ins)]))

        with caplog.at_level(logging.WARNING):
            await service.launch(self.a_request())
            await self.wait_for_the_end(service)

        assert service.flight is not None
        assert service.flight.all_completed is False
        assert len(service.flight.outcomes) == len(stand_ins)
        assert any(record.levelno == logging.WARNING for record in caplog.records)

    async def test_a_second_flight_is_refused_while_the_first_flies_and_close_stops_it(
        self, stand_in_drones: StandInDrones, app_config: partial[Path]
    ) -> None:
        stalled = stand_in_drones.make(stall_after_seq=self.STALL_AFTER_SEQ)
        service = self.a_service(app_config([a_registered_drone(stalled)]))
        await service.launch(self.a_request())

        with pytest.raises(SESimulationRunningError):
            await service.launch(self.a_request())
        await service.close()

        assert service.flying is False
        assert service.task is None

    async def test_close_without_a_flight_does_nothing(
        self, stand_in_drones: StandInDrones, app_config: partial[Path]
    ) -> None:
        service = self.a_service(app_config([a_registered_drone(stand_in_drones.make())]))

        await service.close()

        assert service.task is None
