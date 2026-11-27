from __future__ import annotations

# Standard library imports
import logging
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from swarm_clients.gateway.keycloak.keycloak_admin_client import KeycloakAdminClient
from swarm_models.keycloak.exceptions import SEKeycloakConflictError, SEKeycloakUnreachableError
from swarm_models.keycloak.keycloak_admin_config import KeycloakAdminConfig
from swarm_models.operators.operator import Operator
from swarm_models.people.enums import RoleName
from swarm_models.people.person import Person

from tests.fakes.keycloak.helpers import (  # isort: skip
    ATTRIBUTES_KEY,
    EMAIL_KEY,
    FIRST_NAME_KEY,
    NAME_KEY,
    REQUIRED_ACTIONS_KEY,
    SECRET_ENVIRONMENT_ENTRY,
    USERNAME_KEY,
)
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn  # isort: skip


class TestKeycloakAdminClient:
    OPERATOR_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    OPERATOR_NAME: ClassVar[str] = "Aerowing Services"
    PERSON_NAME: ClassVar[str] = "Ada Lovelace"
    PERSON_EMAIL: ClassVar[str] = "ada@aerowing.example"
    OPERATOR_ID_ATTRIBUTE: ClassVar[str] = "operator_id"
    SIGN_IN_CLIENT_ID: ClassVar[str] = "back-office"
    UPDATE_PASSWORD: ClassVar[str] = "UPDATE_PASSWORD"
    CONFIGURE_TOTP: ClassVar[str] = "CONFIGURE_TOTP"
    UNREACHABLE_URL: ClassVar[str] = "http://127.0.0.1:1"
    WRONG_SECRET: ClassVar[str] = "not-the-secret"
    TIMEOUT_S: ClassVar[float] = 2.0
    MEMBERS_FRAGMENT: ClassVar[str] = "/members"
    USERS_FRAGMENT: ClassVar[str] = "/users"
    ORGANISATIONS_FRAGMENT: ClassVar[str] = "/organizations"

    def operator(self) -> Operator:
        return Operator.model_construct(id=self.OPERATOR_ID, name=self.OPERATOR_NAME)

    def person(self) -> Person:
        return Person(id=self.PERSON_ID, operator_id=self.OPERATOR_ID, name=self.PERSON_NAME, email=self.PERSON_EMAIL)

    def client(self, stand_in: KeycloakAdminStandIn) -> KeycloakAdminClient:
        return KeycloakAdminClient(
            KeycloakAdminConfig(server_url=stand_in.server_url, request_timeout_s=self.TIMEOUT_S)
        )

    def holds_operator(self, value: JsonValue) -> bool:
        return value == str(self.OPERATOR_ID) or value == [str(self.OPERATOR_ID)]

    async def test_an_organisation_is_created_named_after_the_operator(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        identifier = await self.client(keycloak_admin_stand_in).create_organisation(self.operator())
        organisation = keycloak_admin_stand_in.organisations[identifier]
        assert organisation[NAME_KEY] == self.OPERATOR_NAME
        attributes = organisation[ATTRIBUTES_KEY]
        assert isinstance(attributes, dict)
        assert self.holds_operator(attributes[self.OPERATOR_ID_ATTRIBUTE])

    async def test_the_first_mission_planner_is_invited_with_the_required_actions(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        client = self.client(keycloak_admin_stand_in)
        organisation_id = await client.create_organisation(self.operator())
        user_id = await client.invite_mission_planner(organisation_id, self.person())
        user = keycloak_admin_stand_in.users[user_id]
        assert user[EMAIL_KEY] == self.PERSON_EMAIL
        assert user[USERNAME_KEY] == self.PERSON_EMAIL
        assert self.PERSON_NAME in str(user[FIRST_NAME_KEY])
        attributes = user[ATTRIBUTES_KEY]
        assert isinstance(attributes, dict)
        assert self.holds_operator(attributes[self.OPERATOR_ID_ATTRIBUTE])
        required = user[REQUIRED_ACTIONS_KEY]
        assert isinstance(required, list)
        assert sorted(str(action) for action in required) == sorted([self.UPDATE_PASSWORD, self.CONFIGURE_TOTP])

    async def test_the_invited_person_gets_the_mission_planner_role_and_joins_the_organisation(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        client = self.client(keycloak_admin_stand_in)
        organisation_id = await client.create_organisation(self.operator())
        user_id = await client.invite_mission_planner(organisation_id, self.person())
        assert keycloak_admin_stand_in.realm_roles[user_id] == [RoleName.MISSION_PLANNER.value]
        assert keycloak_admin_stand_in.members[organisation_id] == [user_id]

    async def test_the_actions_e_mail_is_sent_once_and_returns_to_the_sign_in_client(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        client = self.client(keycloak_admin_stand_in)
        organisation_id = await client.create_organisation(self.operator())
        user_id = await client.invite_mission_planner(organisation_id, self.person())
        assert len(keycloak_admin_stand_in.action_emails) == 1
        sent_user, actions, client_id = keycloak_admin_stand_in.action_emails[0]
        assert sent_user == user_id
        assert sorted(actions) == sorted([self.UPDATE_PASSWORD, self.CONFIGURE_TOTP])
        assert client_id == self.SIGN_IN_CLIENT_ID

    async def test_an_e_mail_already_used_raises_a_conflict_and_sends_nothing(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        keycloak_admin_stand_in.existing_email(self.PERSON_EMAIL.upper())
        client = self.client(keycloak_admin_stand_in)
        organisation_id = await client.create_organisation(self.operator())
        with pytest.raises(SEKeycloakConflictError):
            await client.invite_mission_planner(organisation_id, self.person())
        assert keycloak_admin_stand_in.action_emails == []
        assert keycloak_admin_stand_in.members == {}

    async def test_a_deleted_organisation_and_a_deleted_user_are_gone(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        client = self.client(keycloak_admin_stand_in)
        organisation_id = await client.create_organisation(self.operator())
        user_id = await client.invite_mission_planner(organisation_id, self.person())
        await client.delete_user(user_id)
        await client.delete_organisation(organisation_id)
        assert user_id not in keycloak_admin_stand_in.users
        assert organisation_id not in keycloak_admin_stand_in.organisations

    @pytest.mark.parametrize("fragment", [ORGANISATIONS_FRAGMENT, USERS_FRAGMENT, MEMBERS_FRAGMENT])
    async def test_a_server_failure_raises_unreachable(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn, fragment: str
    ) -> None:
        keycloak_admin_stand_in.fail_path(fragment)
        client = self.client(keycloak_admin_stand_in)
        with pytest.raises(SEKeycloakUnreachableError):
            organisation_id = await client.create_organisation(self.operator())
            await client.invite_mission_planner(organisation_id, self.person())

    async def test_an_unreachable_server_raises_unreachable(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        config = KeycloakAdminConfig(server_url=self.UNREACHABLE_URL, request_timeout_s=self.TIMEOUT_S)
        with pytest.raises(SEKeycloakUnreachableError):
            await KeycloakAdminClient(config).create_organisation(self.operator())

    async def test_a_missing_secret_entry_raises_unreachable_and_calls_nothing(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(SECRET_ENVIRONMENT_ENTRY)
        with pytest.raises(SEKeycloakUnreachableError):
            await self.client(keycloak_admin_stand_in).create_organisation(self.operator())
        assert keycloak_admin_stand_in.organisations == {}
        assert keycloak_admin_stand_in.token_requests == 0

    async def test_a_wrong_secret_raises_unreachable(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(SECRET_ENVIRONMENT_ENTRY, self.WRONG_SECRET)
        with pytest.raises(SEKeycloakUnreachableError):
            await self.client(keycloak_admin_stand_in).create_organisation(self.operator())
        assert keycloak_admin_stand_in.organisations == {}

    async def test_the_secret_is_read_when_the_call_is_made_not_when_the_client_is_built(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv(SECRET_ENVIRONMENT_ENTRY)
        client = self.client(keycloak_admin_stand_in)
        monkeypatch.setenv(SECRET_ENVIRONMENT_ENTRY, keycloak_admin_stand_in.client_secret)
        identifier = await client.create_organisation(self.operator())
        assert identifier in keycloak_admin_stand_in.organisations

    async def test_neither_the_secret_nor_a_token_is_ever_logged(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        client = self.client(keycloak_admin_stand_in)
        organisation_id = await client.create_organisation(self.operator())
        await client.invite_mission_planner(organisation_id, self.person())
        keycloak_admin_stand_in.fail_path(self.USERS_FRAGMENT)
        with pytest.raises(SEKeycloakUnreachableError):
            await client.delete_user(organisation_id)
        logged: List[str] = [record.getMessage() for record in caplog.records]
        assert logged
        assert all(keycloak_admin_stand_in.client_secret not in line for line in logged)
        assert all(token not in line for token in keycloak_admin_stand_in.tokens for line in logged)
