from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import ClassVar

# Third-party imports
import pytest
from fastapi.testclient import TestClient

# First-party imports
from missions.api.rest.missions_rest_app import MissionsRestApp
from missions.models.config.missions_config import MissionsConfig
from swarm_rest.models.problems.problem import Problem


class TestMissionsRestApp:
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    UNKNOWN_PATH: ClassVar[str] = "/v1/nothing"
    PROBLEM_SCHEMA: ClassVar[str] = "Problem"
    OPENAPI_OUTPUT: ClassVar[str] = "packages/ts/api-client/openapi/missions.json"
    REPOSITORY_ROOT_DEPTH: ClassVar[int] = 5

    @pytest.fixture
    def client(self) -> TestClient:
        return TestClient(MissionsRestApp(MissionsConfig()).build())

    def test_the_class_variables_name_the_title_and_the_published_file(self) -> None:
        assert MissionsRestApp.TITLE
        assert MissionsRestApp.OPENAPI_OUTPUT == self.OPENAPI_OUTPUT

    def test_the_openapi_document_is_served_under_v1(self, client: TestClient) -> None:
        response = client.get(self.OPENAPI_PATH)

        assert response.status_code == 200
        document = response.json()
        assert document["openapi"].startswith("3.1")
        assert document["info"]["title"] == MissionsRestApp.TITLE
        assert self.PROBLEM_SCHEMA in document["components"]["schemas"]

    def test_an_unknown_path_gives_a_problem_json_404(self, client: TestClient) -> None:
        response = client.get(self.UNKNOWN_PATH)

        assert response.status_code == 404
        assert response.headers["content-type"].startswith(Problem.MEDIA_TYPE)
        assert response.json()["status"] == 404

    def test_a_post_without_an_idempotency_key_gives_a_problem_json_400(self, client: TestClient) -> None:
        response = client.post(self.UNKNOWN_PATH)

        assert response.status_code == 400
        assert response.headers["content-type"].startswith(Problem.MEDIA_TYPE)

    def test_the_published_openapi_document_is_up_to_date(self) -> None:
        root = Path(__file__).resolve().parents[self.REPOSITORY_ROOT_DEPTH]
        published = root / MissionsRestApp.OPENAPI_OUTPUT
        app = MissionsRestApp(MissionsConfig()).build()
        expected = json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"

        assert published.is_file(), f"{published} is missing. Run `uv run swarm-missions-openapi`."
        assert published.read_text(encoding="utf-8") == expected, (
            f"{published} is out of date. Run `uv run swarm-missions-openapi`."
        )
