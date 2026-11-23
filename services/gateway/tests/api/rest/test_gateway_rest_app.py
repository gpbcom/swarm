from __future__ import annotations

# Standard library imports
import json
from http import HTTPStatus
from pathlib import Path
from typing import ClassVar

# Third-party imports
from fastapi.testclient import TestClient

# First-party imports
from gateway.api.rest.gateway_rest_app import GatewayRestApp
from gateway.models.config.gateway_config import GatewayConfig
from swarm_rest.models.problems.problem import Problem


class TestGatewayRestApp:
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
    ROOT_PARENT_INDEX: ClassVar[int] = 5
    STALE_MESSAGE: ClassVar[str] = "The published OpenAPI document is stale. Run `uv run swarm-gateway-openapi`."

    def build_client(self) -> TestClient:
        return TestClient(GatewayRestApp(GatewayConfig()).build())

    def test_the_openapi_document_is_served_under_v1(self) -> None:
        response = self.build_client().get(self.OPENAPI_PATH)

        assert response.status_code == HTTPStatus.OK
        document = response.json()
        assert document[self.OPENAPI_FIELD].startswith(self.OPENAPI_VERSION_PREFIX)
        assert document[self.INFO_FIELD][self.TITLE_FIELD] == GatewayRestApp.TITLE
        assert self.PROBLEM_SCHEMA in document[self.COMPONENTS_FIELD][self.SCHEMAS_FIELD]

    def test_an_unknown_path_is_a_problem_json_404(self) -> None:
        response = self.build_client().get(self.UNKNOWN_PATH)

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.headers[self.CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)
        assert response.json()[self.STATUS_FIELD] == HTTPStatus.NOT_FOUND

    def test_a_post_without_an_idempotency_key_is_a_problem_json_400(self) -> None:
        response = self.build_client().post(self.UNKNOWN_PATH)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.headers[self.CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)

    def test_the_published_openapi_document_is_up_to_date(self) -> None:
        root = Path(__file__).resolve().parents[self.ROOT_PARENT_INDEX]
        published = root / GatewayRestApp.OPENAPI_OUTPUT
        app = GatewayRestApp(GatewayConfig()).build()
        expected = json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

        assert published.exists(), self.STALE_MESSAGE
        assert published.read_text(encoding=self.ENCODING) == expected, self.STALE_MESSAGE
