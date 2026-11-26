from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar

# Third-party imports
import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

# First-party imports
from swarm_api.v1.fleet.fleet_router import FleetRouter
from swarm_models.config.fleet.fleet_config import FleetConfig
from swarm_models.rest.problems.problem import Problem


class TestFleetRouter:
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    UNKNOWN_PATH: ClassVar[str] = "/v1/nothing"
    PROBLEM_SCHEMA: ClassVar[str] = "Problem"
    TITLE: ClassVar[str] = "Swarm fleet"
    CONTENT_TYPE_KEY: ClassVar[str] = "content-type"
    STATUS_KEY: ClassVar[str] = "status"
    OPENAPI_KEY: ClassVar[str] = "openapi"
    INFO_KEY: ClassVar[str] = "info"
    TITLE_KEY: ClassVar[str] = "title"
    COMPONENTS_KEY: ClassVar[str] = "components"
    SCHEMAS_KEY: ClassVar[str] = "schemas"
    OPENAPI_VERSION_PREFIX: ClassVar[str] = "3.1"

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(FleetRouter(FleetConfig()).application())

    def test_the_router_is_a_router_titled_after_the_app(self) -> None:
        assert isinstance(FleetRouter(FleetConfig()), APIRouter)
        assert FleetRouter.TITLE == self.TITLE

    def test_the_openapi_document_is_served_under_v1(self, client: TestClient) -> None:
        response = client.get(self.OPENAPI_PATH)

        assert response.status_code == HTTPStatus.OK
        document = response.json()
        assert document[self.OPENAPI_KEY].startswith(self.OPENAPI_VERSION_PREFIX)
        assert document[self.INFO_KEY][self.TITLE_KEY] == FleetRouter.TITLE
        assert self.PROBLEM_SCHEMA in document[self.COMPONENTS_KEY][self.SCHEMAS_KEY]

    def test_an_unknown_path_gives_a_problem_json_404(self, client: TestClient) -> None:
        response = client.get(self.UNKNOWN_PATH)

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.headers[self.CONTENT_TYPE_KEY].startswith(Problem.MEDIA_TYPE)
        assert response.json()[self.STATUS_KEY] == HTTPStatus.NOT_FOUND

    def test_a_post_without_an_idempotency_key_gives_a_problem_json_400(self, client: TestClient) -> None:
        response = client.post(self.UNKNOWN_PATH)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.headers[self.CONTENT_TYPE_KEY].startswith(Problem.MEDIA_TYPE)
        assert response.json()[self.STATUS_KEY] == HTTPStatus.BAD_REQUEST
