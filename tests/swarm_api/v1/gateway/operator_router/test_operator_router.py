from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import httpx

# First-party imports
from swarm_models.enums import Jurisdiction
from swarm_models.people.enums import RoleName
from swarm_models.rest.problems.problem import Problem
from tests.fakes.keycloak.keycloak_stand_in import KeycloakStandIn
from tests.swarm_api.v1.gateway.operator_router.helpers import (
    ADMINISTRATOR_ID,
    AEROWING_NAME,
    AEROWING_PLANNER_EMAIL,
    CELL_ASSIGNMENT_FIELD,
    CONTENT_TYPE,
    DETAIL_FIELD,
    FIRST_MISSION_PLANNER_FIELD,
    ID_FIELD,
    MISSING_OPERATOR,
    NAME_FIELD,
    OPERATOR_FIELD,
    OPERATOR_ID_FIELD,
    OPERATOR_PATH_TEMPLATE,
    OPERATORS_PATH,
    OUTSIDER_ID,
    OUTSIDER_OPERATOR_ID,
    aerowing_body,
    bearer,
    mint,
    post_headers,
)


class TestOperatorRouter:
    JURISDICTIONS_FIELD: ClassVar[str] = "jurisdictions"
    EMAIL_FIELD: ClassVar[str] = "email"

    def administrator(self, stand_in: KeycloakStandIn) -> str:
        return mint(stand_in, ADMINISTRATOR_ID, None, RoleName.SWARM_ADMINISTRATOR)

    def planner(self, stand_in: KeycloakStandIn) -> str:
        return mint(stand_in, OUTSIDER_ID, OUTSIDER_OPERATOR_ID, RoleName.MISSION_PLANNER)

    async def test_the_administrator_creates_an_operator(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.administrator(keycloak_stand_in)

        response = await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers(token))

        assert response.status_code == HTTPStatus.CREATED
        created = response.json()
        operator_id = created[OPERATOR_FIELD][ID_FIELD]
        assert created[OPERATOR_FIELD][NAME_FIELD] == AEROWING_NAME
        assert created[CELL_ASSIGNMENT_FIELD][OPERATOR_ID_FIELD] == operator_id
        assert created[FIRST_MISSION_PLANNER_FIELD][OPERATOR_ID_FIELD] == operator_id
        assert created[FIRST_MISSION_PLANNER_FIELD][self.EMAIL_FIELD] == AEROWING_PLANNER_EMAIL

    async def test_a_creation_without_a_jurisdiction_is_a_422_that_names_it(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.administrator(keycloak_stand_in)
        none: List[Jurisdiction] = []

        response = await client.post(OPERATORS_PATH, json=aerowing_body(none), headers=post_headers(token))

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.headers[CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)
        assert self.JURISDICTIONS_FIELD in response.json()[DETAIL_FIELD]

    async def test_a_name_already_taken_is_a_problem_json_409(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.administrator(keycloak_stand_in)
        await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers(token))

        response = await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers(token))

        assert response.status_code == HTTPStatus.CONFLICT
        assert response.headers[CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)

    async def test_a_creation_without_a_token_is_a_401(self, client: httpx.AsyncClient) -> None:
        response = await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers("none"))

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_a_mission_planner_cannot_create_an_operator(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.planner(keycloak_stand_in)

        response = await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers(token))

        assert response.status_code == HTTPStatus.FORBIDDEN

    async def test_a_creation_without_an_idempotency_key_is_a_400(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.administrator(keycloak_stand_in)

        response = await client.post(OPERATORS_PATH, json=aerowing_body(), headers=bearer(token))

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.headers[CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)

    async def test_the_administrator_lists_the_operators(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.administrator(keycloak_stand_in)
        await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers(token))

        response = await client.get(OPERATORS_PATH, headers=bearer(token))

        assert response.status_code == HTTPStatus.OK
        assert [entry[OPERATOR_FIELD][NAME_FIELD] for entry in response.json()] == [AEROWING_NAME]

    async def test_a_mission_planner_cannot_list_the_operators(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        response = await client.get(OPERATORS_PATH, headers=bearer(self.planner(keycloak_stand_in)))

        assert response.status_code == HTTPStatus.FORBIDDEN

    async def test_a_person_reads_her_own_operator(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        admin_token = self.administrator(keycloak_stand_in)
        created = await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers(admin_token))
        operator_id = created.json()[OPERATOR_FIELD][ID_FIELD]
        token = mint(keycloak_stand_in, OUTSIDER_ID, UUID(operator_id), RoleName.MISSION_PLANNER)

        response = await client.get(OPERATOR_PATH_TEMPLATE.format(operator_id=operator_id), headers=bearer(token))

        assert response.status_code == HTTPStatus.OK
        assert response.json()[NAME_FIELD] == AEROWING_NAME

    async def test_another_operators_id_is_not_found(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.planner(keycloak_stand_in)

        response = await client.get(OPERATOR_PATH_TEMPLATE.format(operator_id=MISSING_OPERATOR), headers=bearer(token))

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.headers[CONTENT_TYPE].startswith(Problem.MEDIA_TYPE)

    async def test_the_administrator_has_no_access_to_an_operators_data(
        self, client: httpx.AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.administrator(keycloak_stand_in)
        created = await client.post(OPERATORS_PATH, json=aerowing_body(), headers=post_headers(token))
        operator_id = created.json()[OPERATOR_FIELD][ID_FIELD]

        response = await client.get(OPERATOR_PATH_TEMPLATE.format(operator_id=operator_id), headers=bearer(token))

        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_the_directory_needs_a_token(self, client: httpx.AsyncClient) -> None:
        response = await client.get(OPERATORS_PATH)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
