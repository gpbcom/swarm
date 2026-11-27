from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import httpx
from pydantic import JsonValue

# First-party imports
from swarm_models.people.enums import RoleName
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn
from tests.fakes.keycloak.keycloak_stand_in import KeycloakStandIn
from tests.swarm_api.v1.gateway.operator_router.helpers import (
    ADMINISTRATOR_ID,
    AEROWING_NAME,
    AEROWING_PLANNER_EMAIL,
    ATTRIBUTES_FIELD,
    ID_FIELD,
    NAME_FIELD,
    OPERATOR_FIELD,
    OPERATOR_ID_ATTRIBUTE,
    OPERATOR_PATH_TEMPLATE,
    OPERATORS_PATH,
    SKYLINE_NAME,
    SKYLINE_PLANNER_EMAIL,
    aerowing_body,
    bearer,
    mint,
    post_headers,
    skyline_body,
)


class TestOperatorIsolation:
    EMAIL_FIELD: ClassVar[str] = "email"

    async def create(self, client: httpx.AsyncClient, token: str, body: Dict[str, JsonValue]) -> UUID:
        response = await client.post(OPERATORS_PATH, json=body, headers=post_headers(token))
        assert response.status_code == HTTPStatus.CREATED
        return UUID(response.json()[OPERATOR_FIELD][ID_FIELD])

    def planner_of(self, admin: KeycloakAdminStandIn, email: str, operator_id: UUID) -> UUID:
        matches = [(user_id, user) for user_id, user in admin.users.items() if user[self.EMAIL_FIELD] == email]
        assert len(matches) == 1
        user_id, user = matches[0]
        assert user[ATTRIBUTES_FIELD][OPERATOR_ID_ATTRIBUTE] == [str(operator_id)]
        assert RoleName.MISSION_PLANNER.value in admin.realm_roles[user_id]
        assert any(sent[0] == user_id for sent in admin.action_emails)
        return UUID(user_id)

    async def test_an_operator_never_reaches_another_operators_data(
        self,
        client: httpx.AsyncClient,
        keycloak_stand_in: KeycloakStandIn,
        keycloak_admin_stand_in: KeycloakAdminStandIn,
    ) -> None:
        administrator = mint(keycloak_stand_in, ADMINISTRATOR_ID, None, RoleName.SWARM_ADMINISTRATOR)
        aerowing_id = await self.create(client, administrator, aerowing_body())
        skyline_id = await self.create(client, administrator, skyline_body())
        aerowing_planner = self.planner_of(keycloak_admin_stand_in, AEROWING_PLANNER_EMAIL, aerowing_id)
        skyline_planner = self.planner_of(keycloak_admin_stand_in, SKYLINE_PLANNER_EMAIL, skyline_id)
        aerowing_token = mint(keycloak_stand_in, aerowing_planner, aerowing_id, RoleName.MISSION_PLANNER)
        skyline_token = mint(keycloak_stand_in, skyline_planner, skyline_id, RoleName.MISSION_PLANNER)

        own = await client.get(OPERATOR_PATH_TEMPLATE.format(operator_id=aerowing_id), headers=bearer(aerowing_token))
        other = await client.get(OPERATOR_PATH_TEMPLATE.format(operator_id=skyline_id), headers=bearer(aerowing_token))
        directory = await client.get(OPERATORS_PATH, headers=bearer(aerowing_token))
        reverse_own = await client.get(
            OPERATOR_PATH_TEMPLATE.format(operator_id=skyline_id), headers=bearer(skyline_token)
        )
        reverse_other = await client.get(
            OPERATOR_PATH_TEMPLATE.format(operator_id=aerowing_id), headers=bearer(skyline_token)
        )
        reverse_directory = await client.get(OPERATORS_PATH, headers=bearer(skyline_token))

        assert own.status_code == HTTPStatus.OK
        assert own.json()[NAME_FIELD] == AEROWING_NAME
        assert other.status_code == HTTPStatus.NOT_FOUND
        assert directory.status_code == HTTPStatus.FORBIDDEN
        assert reverse_own.status_code == HTTPStatus.OK
        assert reverse_own.json()[NAME_FIELD] == SKYLINE_NAME
        assert reverse_other.status_code == HTTPStatus.NOT_FOUND
        assert reverse_directory.status_code == HTTPStatus.FORBIDDEN
