from __future__ import annotations

# Standard library imports
from typing import AsyncIterator

# Third-party imports
import pytest
from pytest import MonkeyPatch

# First-party imports
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_service.gateway.operators.operator_service import OperatorService
from swarm_storage.shared.postgres.postgres_pool import PostgresPool
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn
from tests.swarm_service.gateway.operators.operator_service.helpers import a_pool, a_service, create_directory


@pytest.fixture
async def service(
    monkeypatch: MonkeyPatch, postgres_dsn: str, keycloak_admin_stand_in: KeycloakAdminStandIn
) -> AsyncIterator[OperatorService]:
    monkeypatch.setenv(PostgresConfig().dsn_key, postgres_dsn)
    await create_directory(postgres_dsn)
    built = a_service(a_pool(), keycloak_admin_stand_in)
    yield built
    await built.close()


@pytest.fixture
async def reading_pool(service: OperatorService) -> AsyncIterator[PostgresPool]:
    opened = a_pool()
    await opened.open()
    yield opened
    await opened.close()
