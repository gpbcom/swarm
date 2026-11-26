from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, List

# Third-party imports
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

# First-party imports
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_models.rest.problems.problem import Problem
from swarm_web.models.rest.exceptions import SEPreconditionRequiredError
from tests.swarm_web.rest.sample_resource import SampleResource


class TestProblemHandlers:
    CONTENT_TYPE: ClassVar[str] = "content-type"
    UNKNOWN_PATH: ClassVar[str] = "/nowhere"
    SAMPLE_ONE_PATH: ClassVar[str] = "/samples/1"
    BAD_BODY: ClassVar[List[int]] = [1, 2]

    def client(self) -> TestClient:
        app = FastAPI()
        app.include_router(SampleResource().router)
        ProblemHandlers().install(app)
        return TestClient(app, raise_server_exceptions=False)

    def problem_of(self, response: Response, path: str) -> Problem:
        assert response.headers[self.CONTENT_TYPE] == Problem.MEDIA_TYPE
        problem = Problem.model_validate(response.json())
        assert problem.instance == path
        return problem

    def test_an_unknown_path_gives_a_404_problem(self) -> None:
        response = self.client().get(self.UNKNOWN_PATH)
        problem = self.problem_of(response, self.UNKNOWN_PATH)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert problem.status == HTTPStatus.NOT_FOUND

    def test_an_http_exception_gives_its_status_and_detail(self) -> None:
        response = self.client().get(SampleResource.ABSENT_PATH)
        problem = self.problem_of(response, SampleResource.ABSENT_PATH)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert problem.detail == SampleResource.ABSENT_DETAIL

    def test_an_unexpected_error_gives_a_500_without_its_detail(self) -> None:
        response = self.client().get(SampleResource.CRASH_PATH)
        problem = self.problem_of(response, SampleResource.CRASH_PATH)
        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert problem.title == HTTPStatus.INTERNAL_SERVER_ERROR.phrase
        assert problem.detail is None
        assert SampleResource.SECRET_DETAIL not in response.text

    def test_a_bad_request_body_gives_a_422_problem(self) -> None:
        response = self.client().post(SampleResource.SAMPLES_PATH, json=self.BAD_BODY)
        self.problem_of(response, SampleResource.SAMPLES_PATH)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_a_rest_error_gives_its_status_and_title(self) -> None:
        response = self.client().put(self.SAMPLE_ONE_PATH)
        problem = self.problem_of(response, self.SAMPLE_ONE_PATH)
        assert response.status_code == SEPreconditionRequiredError.STATUS
        assert problem.status == SEPreconditionRequiredError.STATUS
        assert problem.title == SEPreconditionRequiredError.TITLE
