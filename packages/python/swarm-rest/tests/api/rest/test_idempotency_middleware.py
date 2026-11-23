from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, Dict, List, Tuple

# Third-party imports
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import JsonValue
from samples.sample_resource import SampleResource

# First-party imports
from swarm_rest.api.rest.idempotency_middleware import IdempotencyMiddleware
from swarm_rest.api.rest.problem_handlers import ProblemHandlers
from swarm_rest.models.config.rest_config import RestConfig
from swarm_rest.models.problems.problem import Problem
from swarm_rest.service.factories.idempotency_service_factory import IdempotencyServiceFactory


class TestIdempotencyMiddleware:
    CONTENT_TYPE: ClassVar[str] = "content-type"
    KEY: ClassVar[str] = "key-1"
    OTHER_KEY: ClassVar[str] = "key-2"
    TOO_LONG_KEY: ClassVar[str] = "k" * 256
    KEY_WITH_SPACE: ClassVar[str] = "a key"
    BODY: ClassVar[Dict[str, JsonValue]] = {"name": "first"}
    OTHER_BODY: ClassVar[Dict[str, JsonValue]] = {"name": "second"}

    def build(self) -> Tuple[TestClient, SampleResource]:
        resource = SampleResource()
        app = FastAPI()
        app.include_router(resource.router)
        ProblemHandlers().install(app)
        app.add_middleware(IdempotencyMiddleware, service=IdempotencyServiceFactory(RestConfig()).create())
        return TestClient(app, raise_server_exceptions=False), resource

    def headers(self, key: str) -> Dict[str, str]:
        return {IdempotencyMiddleware.IDEMPOTENCY_KEY_HEADER: key}

    def test_the_header_name_is_idempotency_key(self) -> None:
        assert IdempotencyMiddleware.IDEMPOTENCY_KEY_HEADER == "Idempotency-Key"

    def test_a_post_without_the_header_gives_a_400_problem(self) -> None:
        client, resource = self.build()
        response = client.post(SampleResource.SAMPLES_PATH, json=self.BODY)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.headers[self.CONTENT_TYPE] == Problem.MEDIA_TYPE
        assert resource.post_runs == 0

    @pytest.mark.parametrize("key", [TOO_LONG_KEY, KEY_WITH_SPACE])
    def test_an_invalid_key_gives_a_400(self, key: str) -> None:
        client, resource = self.build()
        response = client.post(SampleResource.SAMPLES_PATH, json=self.BODY, headers=self.headers(key))
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert resource.post_runs == 0

    def test_the_same_key_and_body_replay_the_first_answer(self) -> None:
        client, resource = self.build()
        first = client.post(SampleResource.SAMPLES_PATH, json=self.BODY, headers=self.headers(self.KEY))
        second = client.post(SampleResource.SAMPLES_PATH, json=self.BODY, headers=self.headers(self.KEY))
        assert first.status_code == second.status_code == HTTPStatus.CREATED
        assert first.content == second.content
        assert resource.post_runs == 1

    def test_the_same_key_with_another_body_gives_a_422(self) -> None:
        client, resource = self.build()
        client.post(SampleResource.SAMPLES_PATH, json=self.BODY, headers=self.headers(self.KEY))
        response = client.post(SampleResource.SAMPLES_PATH, json=self.OTHER_BODY, headers=self.headers(self.KEY))
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.headers[self.CONTENT_TYPE] == Problem.MEDIA_TYPE
        assert resource.post_runs == 1

    def test_a_503_is_not_stored_so_a_retry_runs_again(self) -> None:
        client, resource = self.build()
        responses: List[int] = []
        for _ in range(2):
            response = client.post(SampleResource.FAILURES_PATH, json=self.BODY, headers=self.headers(self.KEY))
            responses.append(response.status_code)
        assert responses == [HTTPStatus.SERVICE_UNAVAILABLE] * 2
        assert resource.failure_runs == 2

    def test_a_get_needs_no_key(self) -> None:
        client, _ = self.build()
        response = client.get(SampleResource.ABSENT_PATH)
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_two_different_keys_run_the_route_twice(self) -> None:
        client, resource = self.build()
        client.post(SampleResource.SAMPLES_PATH, json=self.BODY, headers=self.headers(self.KEY))
        client.post(SampleResource.SAMPLES_PATH, json=self.BODY, headers=self.headers(self.OTHER_KEY))
        assert resource.post_runs == 2
