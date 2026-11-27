from __future__ import annotations

# Standard library imports
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, List, Optional
from uuid import UUID

# Third-party imports
import asyncpg
from fastapi import FastAPI
from pydantic import JsonValue

# First-party imports
from swarm_clients.gateway.keycloak.keycloak_admin_client import KeycloakAdminClient
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.keycloak.keycloak_admin_config import KeycloakAdminConfig
from swarm_models.operators.operator_entry import OperatorEntry
from swarm_service.gateway.operators.operator_service import OperatorService
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.shared.postgres.postgres_pool import PostgresPool
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn

EVENT_ENTERED = "inner entered"
EVENT_LEFT = "inner left"
SCHEMA = "gateway"
CELL = "eu_west"
OPERATOR_NAME = "Aerowing Services"
PLANNER_NAME = "Amelia Rossi"
PLANNER_EMAIL = "amelia.rossi@aerowing.example"
OTHER_OPERATOR_NAME = "Borealis Drones"
OTHER_PLANNER_EMAIL = "bjorn.larsen@borealis.example"
OPERATOR_ID_ATTRIBUTE = "operator_id"
ORGANISATIONS_PATH = "organizations"
USERS_PATH = "users"
ROLE_MAPPINGS_PATH = "role-mappings"
MEMBERS_PATH = "members"
ACTIONS_EMAIL_PATH = "execute-actions-email"
CREATE_SCHEMA = f"CREATE SCHEMA {SCHEMA}"
COUNT_OPERATORS = f"SELECT count(*) FROM {SCHEMA}.operators"
COUNT_CELL_ASSIGNMENTS = f"SELECT count(*) FROM {SCHEMA}.cell_assignments"


def an_entry(
    name: Optional[str] = OPERATOR_NAME,
    deployment: Optional[Deployment] = Deployment.CLOUD,
    jurisdictions: Optional[List[Jurisdiction]] = None,
    llm_provider: Optional[LlmProvider] = None,
    anchoring: Anchoring = Anchoring.QUALIFIED_TIMESTAMPING,
    planner_name: Optional[str] = PLANNER_NAME,
    planner_email: Optional[str] = PLANNER_EMAIL,
) -> OperatorEntry:
    return OperatorEntry(
        name=name,
        deployment=deployment,
        jurisdictions=[Jurisdiction.EU_EASA] if jurisdictions is None else jurisdictions,
        llm_provider=llm_provider,
        anchoring=anchoring,
        first_mission_planner_name=planner_name,
        first_mission_planner_email=planner_email,
    )


def keycloak_config_of(stand_in: KeycloakAdminStandIn) -> KeycloakAdminConfig:
    return KeycloakAdminConfig(server_url=stand_in.server_url, realm=stand_in.realm, client_id=stand_in.client_id)


def a_service(pool: PostgresPool, stand_in: KeycloakAdminStandIn) -> OperatorService:
    return OperatorService(pool, SCHEMA, CELL, KeycloakAdminClient(keycloak_config_of(stand_in)))


def a_pool() -> PostgresPool:
    return PostgresPool(PostgresConfig())


async def create_directory(dsn: str) -> None:
    connection = await asyncpg.connect(dsn)
    await connection.execute(CREATE_SCHEMA)
    for statement in OperatorDirectoryTables().create(SCHEMA):
        await connection.execute(statement)
    await connection.close()


async def count_rows(dsn: str, query: str) -> int:
    connection = await asyncpg.connect(dsn)
    count: int = await connection.fetchval(query)
    await connection.close()
    return count


def attribute_of(user: Dict[str, JsonValue], key: str) -> Optional[str]:
    attributes = user.get("attributes")
    if not isinstance(attributes, dict):
        return None
    value = attributes.get(key)
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value is not None else None


def operator_id_of(user: Dict[str, JsonValue]) -> Optional[UUID]:
    found = attribute_of(user, OPERATOR_ID_ATTRIBUTE)
    return UUID(found) if found else None


@asynccontextmanager
async def recording_lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.events.append(EVENT_ENTERED)
    yield
    app.state.events.append(EVENT_LEFT)
