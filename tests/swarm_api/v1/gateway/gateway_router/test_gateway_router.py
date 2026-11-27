from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar

# Third-party imports
from fastapi import APIRouter
from fastapi.testclient import TestClient

# First-party imports
from swarm_api.v1.gateway.gateway_router import GatewayRouter
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.rest.problems.problem import Problem


class TestGatewayRouter:
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    UNKNOWN_PATH: ClassVar[str] = "/v1/nothing"
    CONTENT_TYPE: ClassVar[str] = "content-type"
    OPENAPI_VERSION_PREFIX: ClassVar[str] = "3.1"
    PROBLEM_SCHEMA: ClassVar[str] = "Problem"
    STATUS_FIELD: ClassVar[str] = "status"
    OPENAPI_FIELD: ClassVar[str] = "openapi"
    INFO_FIELD: ClassVar[str] = "info"
    TITLE_FIELD: ClassVar[str] = "title"
    COMPONENTS_FIELD: ClassVar[str] = "components"
    SCHEMAS_FIELD: ClassVar[str] = "schemas"
    ENCODING: ClassVar[str] = "utf-8"
    PATHS_FIELD: ClassVar[str] = "paths"
    OPERATORS_PATH: ClassVar[str] = "/v1/operators"
    OPERATOR_PATH: ClassVar[str] = "/v1/operators/{operator_id}"

    def build_client(self) -> TestClient:
        return TestClient(GatewayRouter(GatewayConfig()).application())

    def test_the_router_is_a_router(self) -> None:
        assert isinstance(GatewayRouter(GatewayConfig()), APIRouter)

    def test_the_openapi_document_is_served_under_v1(self) -> None:
        response = self.build_client().get(self.OPENAPI_PATH)

        assert response.status_code == HTTPStatus.OK
        document = response.json()
        assert document[self.OPENAPI_FIELD].startswith(self.OPENAPI_VERSION_PREFIX)
        assert document[self.INFO_FIELD][self.TITLE_FIELD] == GatewayRouter.TITLE
        assert self.PROBLEM_SCHEMA in document[self.COMPONENTS_FIELD][self.SCHEMAS_FIELD]

    def test_the_openapi_document_lists_the_operator_routes(self) -> None:
        document = self.build_client().get(self.OPENAPI_PATH).json()

        assert self.OPERATORS_PATH in document[self.PATHS_FIELD]
        assert self.OPERATOR_PATH in document[self.PATHS_FIELD]

    def test_an_unknown_path_is_a_problem_json_404(self) -> None:
        response = self.build_client().get(self.UNKNOWN_PATH)

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.headers[self.CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)
        assert response.json()[self.STATUS_FIELD] == HTTPStatus.NOT_FOUND

    def test_a_post_without_an_idempotency_key_is_a_problem_json_400(self) -> None:
        response = self.build_client().post(self.UNKNOWN_PATH)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.headers[self.CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)
