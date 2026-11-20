from __future__ import annotations

from http import HTTPStatus
from typing import Annotated, ClassVar, Dict, Optional

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import JsonValue

from swarm_rest.api.rest.entity_tag import EntityTag


class SampleResource:
    """A small REST resource that exercises the conventions of ``swarm_rest``.

    Attributes:
        VERSION (int): The row version the resource exposes as its entity tag.
        COUNT_KEY (str): Key of the run counter in the answers.
        SECRET_DETAIL (str): Text of the error ``/crash`` raises, which must never reach a client.
        ABSENT_DETAIL (str): Detail of the 404 that ``/absent`` raises.
        SAMPLES_PATH (str): Path of the collection.
        SAMPLE_PATH (str): Path template of one sample.
        FAILURES_PATH (str): Path of the route that answers 503.
        CRASH_PATH (str): Path of the route that raises an unexpected error.
        ABSENT_PATH (str): Path of the route that raises a 404.
        POST_METHOD (str): The POST method.
        GET_METHOD (str): The GET method.
        PUT_METHOD (str): The PUT method.
        router (APIRouter): The routes of the resource.
        post_runs (int): How many times ``POST /samples`` ran.
        failure_runs (int): How many times ``POST /failures`` ran.
    """

    VERSION: ClassVar[int] = 3
    COUNT_KEY: ClassVar[str] = "count"
    SECRET_DETAIL: ClassVar[str] = "secret detail"
    ABSENT_DETAIL: ClassVar[str] = "No sample has this identifier."
    SAMPLES_PATH: ClassVar[str] = "/samples"
    SAMPLE_PATH: ClassVar[str] = "/samples/{sample_id}"
    FAILURES_PATH: ClassVar[str] = "/failures"
    CRASH_PATH: ClassVar[str] = "/crash"
    ABSENT_PATH: ClassVar[str] = "/absent"
    POST_METHOD: ClassVar[str] = "POST"
    GET_METHOD: ClassVar[str] = "GET"
    PUT_METHOD: ClassVar[str] = "PUT"

    def __init__(self) -> None:
        self.post_runs = 0
        self.failure_runs = 0
        self.router = APIRouter()
        self.router.add_api_route(
            self.SAMPLES_PATH, self.create, methods=[self.POST_METHOD], status_code=HTTPStatus.CREATED
        )
        self.router.add_api_route(self.SAMPLE_PATH, self.read, methods=[self.GET_METHOD])
        self.router.add_api_route(self.SAMPLE_PATH, self.replace, methods=[self.PUT_METHOD])
        self.router.add_api_route(self.FAILURES_PATH, self.fail, methods=[self.POST_METHOD])
        self.router.add_api_route(self.CRASH_PATH, self.crash, methods=[self.GET_METHOD])
        self.router.add_api_route(self.ABSENT_PATH, self.absent, methods=[self.GET_METHOD])

    def create(self, body: Dict[str, JsonValue]) -> Dict[str, int]:
        """Answer 201 with the number of times this route ran."""
        self.post_runs += 1
        return {self.COUNT_KEY: self.post_runs}

    def read(self, sample_id: str) -> Response:
        """Answer 200 with the entity tag of the sample."""
        response = JSONResponse({self.COUNT_KEY: self.VERSION})
        response.headers[EntityTag.ETAG_HEADER] = EntityTag().format(self.VERSION)
        return response

    def replace(self, sample_id: str, if_match: Annotated[Optional[str], Header()] = None) -> Dict[str, int]:
        """Check ``If-Match`` and answer 200."""
        EntityTag().check_if_match(if_match, self.VERSION)
        return {self.COUNT_KEY: self.VERSION}

    def fail(self) -> JSONResponse:
        """Answer 503 and count the run."""
        self.failure_runs += 1
        return JSONResponse({self.COUNT_KEY: self.failure_runs}, status_code=HTTPStatus.SERVICE_UNAVAILABLE)

    def crash(self) -> None:
        """Raise an unexpected error with a secret detail."""
        raise RuntimeError(self.SECRET_DETAIL)

    def absent(self) -> None:
        """Raise a 404."""
        raise HTTPException(HTTPStatus.NOT_FOUND, self.ABSENT_DETAIL)
