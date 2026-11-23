from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import ClassVar, Dict

# Third-party imports
from fastapi.testclient import TestClient

# First-party imports
from fleet.api.rest.fleet_rest_app import FleetRestApp
from fleet.models.config.fleet_config import FleetConfig
from swarm_rest.models.problems.problem import Problem


class TestFleetRestApp:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[5]
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    UNKNOWN_PATH: ClassVar[str] = "/v1/nothing"
    STATUS_KEY: ClassVar[str] = "status"
    CONTENT_TYPE_KEY: ClassVar[str] = "content-type"
    OPENAPI_KEY: ClassVar[str] = "openapi"
    INFO_KEY: ClassVar[str] = "info"
    TITLE_KEY: ClassVar[str] = "title"
    COMPONENTS_KEY: ClassVar[str] = "components"
    SCHEMAS_KEY: ClassVar[str] = "schemas"
    PROBLEM_SCHEMA: ClassVar[str] = "Problem"
    OPENAPI_VERSION_PREFIX: ClassVar[str] = "3.1"
    ENCODING: ClassVar[str] = "utf-8"
    NO_HEADERS: ClassVar[Dict[str, str]] = {}

    def test_the_class_variables_name_the_title_and_the_published_file(self) -> None:
        assert FleetRestApp.TITLE
        assert FleetRestApp.OPENAPI_OUTPUT == "packages/ts/api-client/openapi/fleet.json"

    def test_the_openapi_document_is_served_under_v1(self) -> None:
        client = TestClient(FleetRestApp(FleetConfig()).build())

        response = client.get(self.OPENAPI_PATH)
        document = response.json()

        assert response.status_code == 200
        assert document[self.OPENAPI_KEY].startswith(self.OPENAPI_VERSION_PREFIX)
        assert document[self.INFO_KEY][self.TITLE_KEY] == FleetRestApp.TITLE
        assert self.PROBLEM_SCHEMA in document[self.COMPONENTS_KEY][self.SCHEMAS_KEY]

    def test_an_unknown_path_gives_a_problem_json_404(self) -> None:
        client = TestClient(FleetRestApp(FleetConfig()).build())

        response = client.get(self.UNKNOWN_PATH)

        assert response.status_code == 404
        assert response.headers[self.CONTENT_TYPE_KEY].startswith(Problem.MEDIA_TYPE)
        assert response.json()[self.STATUS_KEY] == 404

    def test_a_post_without_an_idempotency_key_gives_a_problem_json_400(self) -> None:
        client = TestClient(FleetRestApp(FleetConfig()).build())

        response = client.post(self.UNKNOWN_PATH, headers=self.NO_HEADERS)

        assert response.status_code == 400
        assert response.headers[self.CONTENT_TYPE_KEY].startswith(Problem.MEDIA_TYPE)
        assert response.json()[self.STATUS_KEY] == 400

    def test_the_published_openapi_document_is_up_to_date(self) -> None:
        published = self.ROOT / FleetRestApp.OPENAPI_OUTPUT
        app = FleetRestApp(FleetConfig()).build()
        expected = json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

        assert published.is_file(), "Run `uv run swarm-fleet-openapi` to publish the document."
        assert published.read_text(encoding=self.ENCODING) == expected, "Run `uv run swarm-fleet-openapi`."
