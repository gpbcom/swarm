from __future__ import annotations

# Standard library imports
import socket
from typing import AsyncIterator, Dict

# Third-party imports
import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

# First-party imports
from gateway.api.rest.auth.access_installer import AccessInstaller
from gateway.api.rest.auth.route_access import RouteAccess
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.auth.caller import Caller
from swarm_models.people.enums import RoleName

OPERATOR_PROBE_PATH = "/v1/operators/{operator_id}/probe"
PLAIN_PROBE_PATH = "/v1/probe"
BASE_URL = "http://gateway.test"
LOCALHOST = "127.0.0.1"
CALLER_FIELD = "person_id"
ISSUER_PATH = "/realms/swarm"
GET_METHODS = ["GET"]
PLANNER_ACCESS = Depends(RouteAccess([RoleName.MISSION_PLANNER]))


async def probe_operator(operator_id: str, caller: Caller = PLANNER_ACCESS) -> Dict[str, str]:
    return {CALLER_FIELD: str(caller.person_id)}


async def probe_plain(caller: Caller = PLANNER_ACCESS) -> Dict[str, str]:
    return {CALLER_FIELD: str(caller.person_id)}


def build_probe_app(config: AuthConfig) -> FastAPI:
    app = FastAPI()
    AccessInstaller().install(app, config)
    app.add_api_route(OPERATOR_PROBE_PATH, probe_operator, methods=GET_METHODS)
    app.add_api_route(PLAIN_PROBE_PATH, probe_plain, methods=GET_METHODS)
    return app


def closed_issuer_url() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((LOCALHOST, 0))
        port = probe.getsockname()[1]
    return f"http://{LOCALHOST}:{port}{ISSUER_PATH}"


@pytest.fixture
def probe_app(auth_config: AuthConfig) -> FastAPI:
    return build_probe_app(auth_config)


@pytest.fixture
async def client(probe_app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=probe_app), base_url=BASE_URL) as http_client:
        yield http_client


@pytest.fixture
async def unreachable_client(auth_config: AuthConfig) -> AsyncIterator[AsyncClient]:
    config = auth_config.model_copy(update={"issuer_url": closed_issuer_url()})
    app = build_probe_app(config)
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as http_client:
        yield http_client
