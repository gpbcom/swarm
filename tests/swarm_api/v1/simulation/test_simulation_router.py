from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from pathlib import Path
from typing import ClassVar, Dict, Iterator
from uuid import UUID

# Third-party imports
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# First-party imports
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_api.v1.simulation.simulation_router import SimulationRouter
from swarm_models.config.simulator.simulator_config import SimulatorConfig
from swarm_models.rest.problems.problem import Problem
from swarm_models.simulation.simulations.simulation_accepted import SimulationAccepted
from swarm_web.models.rest.exceptions import SEIdempotencyKeyMissingError
from tests.fakes.mavlink.helpers import DRONE_IDS, MISSION_ID, a_registered_drone, write_app_config
from tests.fakes.mavlink.stand_in_drones import StandInDrones


class TestSimulationRouter:
    PATH: ClassVar[str] = "/v1/simulations"
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    PATHS_KEY: ClassVar[str] = "paths"
    POST_KEY: ClassVar[str] = "post"
    RESPONSES_KEY: ClassVar[str] = "responses"
    CONTENT_TYPE_KEY: ClassVar[str] = "content-type"
    MISSION_ID_KEY: ClassVar[str] = "mission_id"
    NOT_A_VERSION_7: ClassVar[str] = "00000000-0000-4000-8000-000000000000"
    STALL_AFTER_SEQ: ClassVar[int] = 2

    @pytest.fixture
    def router(self, stand_in_drones: StandInDrones, tmp_path: Path) -> Iterator[SimulationRouter]:
        stalled = stand_in_drones.make(stall_after_seq=self.STALL_AFTER_SEQ)
        router = SimulationRouter(SimulatorConfig.load(write_app_config(tmp_path, [a_registered_drone(stalled)])))
        yield router

    def an_app(self, router: SimulationRouter) -> FastAPI:
        return ProblemHandlers().application(SimulationRouter.TITLE, SimulationRouter.VERSION, [router])

    def a_body(self, mission_id: str) -> Dict[str, str]:
        return {self.MISSION_ID_KEY: mission_id}

    def test_the_document_of_the_application_has_the_route_answered_with_202(self, router: SimulationRouter) -> None:
        document = TestClient(router.application()).get(self.OPENAPI_PATH).json()

        responses = document[self.PATHS_KEY][self.PATH][self.POST_KEY][self.RESPONSES_KEY]
        assert str(HTTPStatus.ACCEPTED.value) in responses

    def test_a_request_starts_the_flight_and_a_second_one_is_refused_while_it_flies(
        self, router: SimulationRouter
    ) -> None:
        with TestClient(self.an_app(router)) as client:
            first = client.post(self.PATH, json=self.a_body(str(MISSION_ID)))
            second = client.post(self.PATH, json=self.a_body(str(MISSION_ID)))
            assert client.portal is not None
            client.portal.call(router.simulations.close)

        assert first.status_code == HTTPStatus.ACCEPTED
        accepted = SimulationAccepted.model_validate(first.json())
        assert accepted.mission_id == UUID(str(MISSION_ID))
        assert accepted.drone_ids == [UUID(DRONE_IDS[0])]
        assert second.status_code == HTTPStatus.CONFLICT
        assert second.headers[self.CONTENT_TYPE_KEY] == Problem.MEDIA_TYPE

    def test_a_mission_id_that_is_not_a_version_7_uuid_is_refused_with_422(self, router: SimulationRouter) -> None:
        with TestClient(self.an_app(router)) as client:
            response = client.post(self.PATH, json=self.a_body(self.NOT_A_VERSION_7))

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert router.simulations.flying is False

    def test_the_application_needs_an_idempotency_key(self, router: SimulationRouter) -> None:
        response = TestClient(router.application()).post(self.PATH, json=self.a_body(str(MISSION_ID)))

        assert response.status_code == SEIdempotencyKeyMissingError.STATUS
        assert router.simulations.flying is False
