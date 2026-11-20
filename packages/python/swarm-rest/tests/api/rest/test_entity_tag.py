from __future__ import annotations

from http import HTTPStatus
from typing import ClassVar, Dict, Optional

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from samples.sample_resource import SampleResource

from swarm_rest.api.rest.entity_tag import EntityTag
from swarm_rest.api.rest.problem_handlers import ProblemHandlers
from swarm_rest.models.problems.problem import Problem
from swarm_rest.models.rest.exceptions import SEPreconditionFailedError, SEPreconditionRequiredError


class TestEntityTag:
    CONTENT_TYPE: ClassVar[str] = "content-type"
    SAMPLE_ONE_PATH: ClassVar[str] = "/samples/1"
    VERSION: ClassVar[int] = 7
    FORMATTED: ClassVar[str] = '"7"'
    WEAK: ClassVar[str] = 'W/"7"'
    STALE: ClassVar[str] = '"6"'
    LIST: ClassVar[str] = '"6", "7"'
    STAR: ClassVar[str] = "*"

    def client(self) -> TestClient:
        app = FastAPI()
        app.include_router(SampleResource().router)
        ProblemHandlers().install(app)
        return TestClient(app, raise_server_exceptions=False)

    def headers(self, value: str) -> Dict[str, str]:
        return {EntityTag.IF_MATCH_HEADER: value}

    def test_the_header_names_are_the_standard_ones(self) -> None:
        assert EntityTag.ETAG_HEADER == "ETag"
        assert EntityTag.IF_MATCH_HEADER == "If-Match"

    def test_a_version_is_formatted_as_a_quoted_tag(self) -> None:
        assert EntityTag().format(self.VERSION) == self.FORMATTED

    @pytest.mark.parametrize("header", [FORMATTED, LIST, STAR])
    def test_a_matching_header_passes(self, header: str) -> None:
        EntityTag().check_if_match(header, self.VERSION)

    @pytest.mark.parametrize("header", [None, ""])
    def test_a_missing_header_is_required(self, header: Optional[str]) -> None:
        with pytest.raises(SEPreconditionRequiredError):
            EntityTag().check_if_match(header, self.VERSION)

    @pytest.mark.parametrize("header", [STALE, WEAK])
    def test_a_stale_or_weak_tag_fails_the_precondition(self, header: str) -> None:
        with pytest.raises(SEPreconditionFailedError):
            EntityTag().check_if_match(header, self.VERSION)

    def test_a_get_carries_the_entity_tag(self) -> None:
        response = self.client().get(SampleResource.SAMPLE_PATH.format(sample_id=1))
        assert response.status_code == HTTPStatus.OK
        assert response.headers[EntityTag.ETAG_HEADER] == EntityTag().format(SampleResource.VERSION)

    def test_a_put_without_if_match_gives_a_428_problem(self) -> None:
        response = self.client().put(self.SAMPLE_ONE_PATH)
        assert response.status_code == HTTPStatus.PRECONDITION_REQUIRED
        assert response.headers[self.CONTENT_TYPE] == Problem.MEDIA_TYPE

    def test_a_put_with_a_wrong_tag_gives_a_412(self) -> None:
        response = self.client().put(self.SAMPLE_ONE_PATH, headers=self.headers(self.STALE))
        assert response.status_code == HTTPStatus.PRECONDITION_FAILED
        assert response.headers[self.CONTENT_TYPE] == Problem.MEDIA_TYPE

    def test_a_put_with_the_right_tag_gives_a_200(self) -> None:
        tag = EntityTag().format(SampleResource.VERSION)
        response = self.client().put(self.SAMPLE_ONE_PATH, headers=self.headers(tag))
        assert response.status_code == HTTPStatus.OK
