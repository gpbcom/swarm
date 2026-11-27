from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, Dict, List

# Third-party imports
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.trace import SpanKind
from pydantic import JsonValue

# First-party imports
from swarm_models.rest.problems.problem import Problem
from swarm_web.rest.rest_app_builder import RestAppBuilder
from tests.fakes.signals.recorded_signals import RecordedSignals
from tests.swarm_web.rest.sample_resource import SampleResource


class TestRestAppBuilder:
    CONTENT_TYPE: ClassVar[str] = "content-type"
    TITLE: ClassVar[str] = "Sample API"
    VERSION: ClassVar[str] = "1.2.3"
    PREFIX: ClassVar[str] = "/v1"
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    DOCS_PATH: ClassVar[str] = "/v1/docs"
    ROOT_OPENAPI_PATH: ClassVar[str] = "/openapi.json"
    ANYTHING_PATH: ClassVar[str] = "/v1/anything"
    OPENAPI_PREFIX: ClassVar[str] = "3.1"
    PROBLEM_REF: ClassVar[str] = "#/components/schemas/Problem"
    PROBLEM_PROPERTIES: ClassVar[List[str]] = ["type", "title", "status", "detail", "instance"]
    OTHER_MEDIA_TYPE: ClassVar[str] = "application/sample+json"
    BODY: ClassVar[Dict[str, JsonValue]] = {"name": "first"}
    TRACE_ID: ClassVar[str] = "0af7651916cd43dd8448eb211c80319c"
    TRACEPARENT: ClassVar[Dict[str, str]] = {"traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"}
    SECRET: ClassVar[str] = "s3cret"
    BEARER: ClassVar[Dict[str, str]] = {"Authorization": "Bearer s3cret"}
    TOKEN_QUERY: ClassVar[Dict[str, str]] = {"token": "s3cret"}

    def build(self, routers: bool = True, media_type: str = Problem.MEDIA_TYPE) -> FastAPI:
        resources = [SampleResource().router] if routers else []
        return RestAppBuilder().build(self.TITLE, self.VERSION, resources, Problem, media_type)

    def document(self, routers: bool = True, media_type: str = Problem.MEDIA_TYPE) -> Dict[str, JsonValue]:
        response = TestClient(self.build(routers, media_type)).get(self.OPENAPI_PATH)
        assert response.status_code == HTTPStatus.OK
        return response.json()

    def test_the_routes_are_served_under_v1(self) -> None:
        client = TestClient(self.build())
        response = client.post(self.PREFIX + SampleResource.SAMPLES_PATH, json=self.BODY)
        assert response.status_code == HTTPStatus.CREATED

    def test_the_document_and_the_docs_are_under_v1_only(self) -> None:
        client = TestClient(self.build())
        assert client.get(self.OPENAPI_PATH).status_code == HTTPStatus.OK
        assert client.get(self.DOCS_PATH).status_code == HTTPStatus.OK
        assert client.get(self.ROOT_OPENAPI_PATH).status_code == HTTPStatus.NOT_FOUND

    def test_the_document_is_openapi_3_1_with_the_title_and_version(self) -> None:
        document = self.document()
        info = document["info"]
        assert isinstance(info, dict)
        assert str(document["openapi"]).startswith(self.OPENAPI_PREFIX)
        assert info["title"] == self.TITLE
        assert info["version"] == self.VERSION

    def test_the_problem_schema_is_in_the_components(self) -> None:
        components = self.document()["components"]
        assert isinstance(components, dict)
        schemas = components["schemas"]
        assert isinstance(schemas, dict)
        problem = schemas["Problem"]
        assert isinstance(problem, dict)
        assert set(self.PROBLEM_PROPERTIES) <= set(problem["properties"])

    def test_every_operation_has_a_default_problem_response(self) -> None:
        paths = self.document()["paths"]
        assert isinstance(paths, dict)
        operations = [operation for path in paths.values() for operation in path.values()]
        assert operations
        for operation in operations:
            content = operation["responses"]["default"]["content"][Problem.MEDIA_TYPE]
            assert content["schema"]["$ref"] == self.PROBLEM_REF

    def test_the_problem_schema_is_there_without_any_router(self) -> None:
        components = self.document(routers=False)["components"]
        assert isinstance(components, dict)
        schemas = components["schemas"]
        assert isinstance(schemas, dict)
        assert "Problem" in schemas

    def test_the_default_response_takes_the_media_type_it_is_given(self) -> None:
        paths = self.document(media_type=self.OTHER_MEDIA_TYPE)["paths"]
        assert isinstance(paths, dict)
        operations = [operation for path in paths.values() for operation in path.values()]
        assert operations
        for operation in operations:
            assert list(operation["responses"]["default"]["content"]) == [self.OTHER_MEDIA_TYPE]

    def test_the_builder_installs_no_problem_handler_of_its_own(self) -> None:
        response = TestClient(self.build()).post(self.ANYTHING_PATH, json=self.BODY)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.headers[self.CONTENT_TYPE] != Problem.MEDIA_TYPE

    def test_a_request_with_a_traceparent_gives_a_server_span_in_that_trace(
        self, recorded_signals: RecordedSignals
    ) -> None:
        client = TestClient(self.build())
        response = client.post(self.PREFIX + SampleResource.SAMPLES_PATH, json=self.BODY, headers=self.TRACEPARENT)
        assert response.status_code == HTTPStatus.CREATED
        servers = [span for span in recorded_signals.spans() if span.kind == SpanKind.SERVER]
        assert servers
        assert {format(span.context.trace_id, "032x") for span in servers} == {self.TRACE_ID}

    def test_a_secret_in_a_header_or_a_query_reaches_no_span(self, recorded_signals: RecordedSignals) -> None:
        client = TestClient(self.build())
        client.post(
            self.PREFIX + SampleResource.SAMPLES_PATH,
            json=self.BODY,
            headers=self.BEARER,
            params=self.TOKEN_QUERY,
        )
        spans = recorded_signals.spans()
        assert spans
        values = [
            str(value)
            for span in spans
            for value in [
                *(span.attributes or {}).values(),
                *(v for e in span.events for v in (e.attributes or {}).values()),
            ]
        ]
        assert values
        assert not [value for value in values if self.SECRET in value]
