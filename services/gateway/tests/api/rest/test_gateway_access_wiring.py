from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, Iterator, List, Set

# Third-party imports
import httpx
import yaml
from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from httpx import ASGITransport

# First-party imports
from gateway.api.rest.auth.access_installer import AccessInstaller
from gateway.api.rest.auth.route_access import RouteAccess
from gateway.api.rest.gateway_rest_app import GatewayRestApp
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.config.gateway_config import GatewayConfig
from gateway.service.auth.access_service import AccessService
from swarm_rest.models.problems.problem import Problem


class TestGatewayAccessWiring:
    V1_PREFIX: ClassVar[str] = "/v1"
    PARAMETER_OPEN: ClassVar[str] = "{"
    CONTENT_TYPE: ClassVar[str] = "content-type"
    AUTH_FIELD: ClassVar[str] = "auth"
    BASE_URL: ClassVar[str] = "http://gateway"
    ENCODING: ClassVar[str] = "utf-8"

    def build_app(self) -> FastAPI:
        return GatewayRestApp(GatewayConfig()).build()

    def v1_routes(self, app: FastAPI) -> List[APIRoute]:
        return [route for route in app.routes if isinstance(route, APIRoute) and route.path.startswith(self.V1_PREFIX)]

    def dependency_calls(self, dependant: Dependant) -> Iterator[object]:
        for dependency in dependant.dependencies:
            yield dependency.call
            yield from self.dependency_calls(dependency)

    def test_every_v1_route_has_a_route_access_with_a_role(self) -> None:
        app = self.build_app()

        for route in self.v1_routes(app):
            guards = [call for call in self.dependency_calls(route.dependant) if isinstance(call, RouteAccess)]
            assert guards, route.path
            assert all(guard.roles for guard in guards), route.path

    def test_the_built_app_holds_an_access_service(self) -> None:
        app = self.build_app()

        assert isinstance(getattr(app.state, AccessInstaller.ACCESS_SERVICE_STATE), AccessService)

    async def test_a_v1_route_without_a_token_is_a_problem_json_401(self) -> None:
        app = self.build_app()
        paths = [route.path for route in self.v1_routes(app) if self.PARAMETER_OPEN not in route.path]

        async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url=self.BASE_URL) as client:
            for route in self.v1_routes(app):
                if route.path not in paths:
                    continue
                for method in route.methods:
                    response = await client.request(method, route.path)
                    assert response.status_code == HTTPStatus.UNAUTHORIZED, (method, route.path)
                    assert response.headers[self.CONTENT_TYPE].startswith(Problem.MEDIA_TYPE), route.path

    def test_the_app_yaml_auth_section_writes_out_every_field_of_the_auth_config(self) -> None:
        path = GatewayConfig.conf_folder() / GatewayConfig.APP_FILE
        with path.open(encoding=self.ENCODING) as stream:
            data = yaml.safe_load(stream)
        fields: Set[str] = set(AuthConfig.model_fields)

        assert self.AUTH_FIELD in data
        assert set(data[self.AUTH_FIELD]) == fields
        assert AuthConfig.model_validate(data[self.AUTH_FIELD])
