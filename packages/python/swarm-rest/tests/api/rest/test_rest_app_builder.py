from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, Dict, List

# Third-party imports
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import JsonValue
from samples.sample_resource import SampleResource

# First-party imports
from swarm_rest.api.rest.idempotency_middleware import IdempotencyMiddleware
from swarm_rest.api.rest.rest_app_builder import RestAppBuilder
from swarm_rest.models.config.rest_config import RestConfig
from swarm_rest.models.problems.problem import Problem


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
    KEY: ClassVar[str] = "key-1"
    BODY: ClassVar[Dict[str, JsonValue]] = {"name": "first"}

    def build(self, routers: bool = True) -> FastAPI:
        resources = [SampleResource().router] if routers else []
        return RestAppBuilder(RestConfig()).build(self.TITLE, self.VERSION, resources)

    def document(self, routers: bool = True) -> Dict[str, JsonValue]:
        response = TestClient(self.build(routers)).get(self.OPENAPI_PATH)
        assert response.status_code == HTTPStatus.OK
        return response.json()

    def test_the_routes_are_served_under_v1(self) -> None:
        client = TestClient(self.build())
        response = client.post(
            self.PREFIX + SampleResource.SAMPLES_PATH,
            json=self.BODY,
            headers={IdempotencyMiddleware.IDEMPOTENCY_KEY_HEADER: self.KEY},
        )
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

    def test_the_handlers_and_the_middleware_are_installed(self) -> None:
        response = TestClient(self.build()).post(self.ANYTHING_PATH, json=self.BODY)
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.headers[self.CONTENT_TYPE] == Problem.MEDIA_TYPE
