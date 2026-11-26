from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from pathlib import Path
from typing import ClassVar, Iterator, List, Set

# Third-party imports
import httpx
import pytest
import yaml
from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from httpx import ASGITransport

# First-party imports
from swarm_api.dependencies.route_access import RouteAccess
from swarm_api.handlers.access_handlers import AccessHandlers
from swarm_api.v1.gateway.gateway_router import GatewayRouter
from swarm_models.auth.auth_config import AuthConfig
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.rest.problems.problem import Problem
from swarm_service.gateway.auth.access_service import AccessService


class TestGatewayAccessWiring:
    V1_PREFIX: ClassVar[str] = "/v1"
    PARAMETER_OPEN: ClassVar[str] = "{"
    CONTENT_TYPE: ClassVar[str] = "content-type"
    AUTH_FIELD: ClassVar[str] = "auth"
    BASE_URL: ClassVar[str] = "http://gateway"
    ENCODING: ClassVar[str] = "utf-8"
    APP_FOLDER: ClassVar[Path] = Path(__file__).resolve().parents[5] / "backend" / "apps" / "gateway"

    def build_app(self) -> FastAPI:
        return GatewayRouter(GatewayConfig()).application()

    def v1_routes(self, app: FastAPI) -> List[APIRoute]:
        return [route for route in app.routes if isinstance(route, APIRoute) and route.path.startswith(self.V1_PREFIX)]

    def route_accesses(self, dependant: Dependant) -> Iterator[RouteAccess]:
        for dependency in dependant.dependencies:
            if isinstance(dependency.call, RouteAccess):
                yield dependency.call
            yield from self.route_accesses(dependency)

    def test_every_v1_route_has_a_route_access_with_a_role(self) -> None:
        app = self.build_app()

        for route in self.v1_routes(app):
            guards = list(self.route_accesses(route.dependant))
            assert guards, route.path
            assert all(guard.roles for guard in guards), route.path

    def test_the_built_app_holds_an_access_service(self) -> None:
        app = self.build_app()

        assert isinstance(getattr(app.state, AccessHandlers.ACCESS_SERVICE_STATE), AccessService)

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

    def test_the_app_yaml_auth_section_writes_out_every_field_of_the_auth_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(GatewayConfig.APP_ROOT_KEY, str(self.APP_FOLDER))
        path = GatewayConfig.conf_folder() / GatewayConfig.APP_FILE
        with path.open(encoding=self.ENCODING) as stream:
            data = yaml.safe_load(stream)
        fields: Set[str] = set(AuthConfig.model_fields)

        assert self.AUTH_FIELD in data
        assert set(data[self.AUTH_FIELD]) == fields
        assert AuthConfig.model_validate(data[self.AUTH_FIELD])
