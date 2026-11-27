from __future__ import annotations

# Standard library imports
from typing import AsyncIterator

# Third-party imports
import asyncpg
import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport

# First-party imports
from swarm_api.v1.gateway.gateway_router import GatewayRouter
from swarm_models.auth.auth_config import AuthConfig
from swarm_models.config.gateway.gateway_config import GatewayConfig
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn
from tests.fakes.keycloak.keycloak_stand_in import KeycloakStandIn
from tests.swarm_api.v1.gateway.operator_router.helpers import (
    BASE_URL,
    CREATE_SCHEMA,
    KEYCLOAK_FIELD,
    OPERATORS_FIELD,
    SCHEMA,
    SERVER_URL_FIELD,
)


@pytest.fixture
async def gateway_config(
    monkeypatch: pytest.MonkeyPatch,
    postgres_dsn: str,
    keycloak_stand_in: KeycloakStandIn,
    keycloak_admin_stand_in: KeycloakAdminStandIn,
) -> GatewayConfig:
    monkeypatch.setenv(GatewayConfig.DSN_KEY, postgres_dsn)
    connection = await asyncpg.connect(postgres_dsn)
    await connection.execute(CREATE_SCHEMA)
    for statement in OperatorDirectoryTables().create(SCHEMA):
        await connection.execute(statement)
    await connection.close()
    return GatewayConfig.model_validate(
        {
            GatewayConfig.AUTH_FIELD: AuthConfig(issuer_url=keycloak_stand_in.issuer_url),
            GatewayConfig.POSTGRES_FIELD: PostgresConfig(dsn_key=GatewayConfig.DSN_KEY),
            OPERATORS_FIELD: {KEYCLOAK_FIELD: {SERVER_URL_FIELD: keycloak_admin_stand_in.server_url}},
        }
    )


@pytest.fixture
async def gateway_app(gateway_config: GatewayConfig) -> AsyncIterator[FastAPI]:
    app = GatewayRouter(gateway_config).application()
    async with app.router.lifespan_context(app):
        yield app


@pytest.fixture
async def client(gateway_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(transport=ASGITransport(app=gateway_app), base_url=BASE_URL) as http_client:
        yield http_client
