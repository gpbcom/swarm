from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar, List

# Third-party imports
import pytest
from fastapi import FastAPI
from pytest import MonkeyPatch

# First-party imports
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_service.gateway.operators.operator_lifespan import OperatorLifespan
from swarm_storage.shared.postgres.postgres_pool import PostgresPool
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn
from tests.swarm_service.gateway.operators.operator_service.helpers import (
    EVENT_ENTERED,
    EVENT_LEFT,
    a_pool,
    a_service,
    create_directory,
    recording_lifespan,
)


class TestOperatorLifespan:
    BODY: ClassVar[str] = "body"

    @pytest.fixture
    async def opened(
        self, monkeypatch: MonkeyPatch, postgres_dsn: str, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> AsyncIterator[PostgresPool]:
        monkeypatch.setenv(PostgresConfig().dsn_key, postgres_dsn)
        await create_directory(postgres_dsn)
        pool = a_pool()
        yield pool
        await pool.close()

    async def test_the_inner_lifespan_is_entered_and_left_around_the_body(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        app = FastAPI()
        app.state.events = []
        service = a_service(a_pool(), keycloak_admin_stand_in)
        async with OperatorLifespan(service, recording_lifespan).lifespan(app):
            app.state.events.append(self.BODY)
        events: List[str] = app.state.events
        assert events == [EVENT_ENTERED, self.BODY, EVENT_LEFT]

    async def test_a_service_that_was_never_used_closes_cleanly(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        app = FastAPI()
        app.state.events = []
        pool = a_pool()
        async with OperatorLifespan(a_service(pool, keycloak_admin_stand_in), recording_lifespan).lifespan(app):
            assert not pool.is_open
        assert not pool.is_open

    async def test_the_end_of_the_application_closes_the_service(
        self, opened: PostgresPool, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        app = FastAPI()
        app.state.events = []
        service = a_service(opened, keycloak_admin_stand_in)
        async with OperatorLifespan(service, recording_lifespan).lifespan(app):
            await service.list()
            assert opened.is_open
        assert not opened.is_open

    async def test_the_service_is_closed_when_the_block_raises(
        self, opened: PostgresPool, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        app = FastAPI()
        app.state.events = []
        service = a_service(opened, keycloak_admin_stand_in)
        with pytest.raises(RuntimeError):
            async with OperatorLifespan(service, recording_lifespan).lifespan(app):
                await service.list()
                raise RuntimeError
        assert not opened.is_open
