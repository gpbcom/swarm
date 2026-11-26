from __future__ import annotations

# Standard library imports
import logging
from http import HTTPStatus
from typing import ClassVar, Dict, List, Optional, Union
from uuid import UUID, uuid4

# Third-party imports
import pytest
from httpx import AsyncClient

# First-party imports
from gateway.models.enums import AccessRefusal  # isort: skip
from swarm_models.models.people.enums import RoleName  # isort: skip
from services.gateway.tests.support.keycloak.helpers import AUDIENCE, claims_for  # isort: skip
from services.gateway.tests.support.keycloak.keycloak_stand_in import KeycloakStandIn  # isort: skip


class TestRouteAccess:
    AUTHORIZATION: ClassVar[str] = "Authorization"
    WWW_AUTHENTICATE: ClassVar[str] = "WWW-Authenticate"
    CONTENT_TYPE: ClassVar[str] = "Content-Type"
    PROBLEM_JSON: ClassVar[str] = "application/problem+json"
    BEARER: ClassVar[str] = "Bearer"
    BASIC: ClassVar[str] = "Basic"
    STATUS_KEY: ClassVar[str] = "status"
    TYPE_KEY: ClassVar[str] = "type"
    TITLE_KEY: ClassVar[str] = "title"
    DETAIL_KEY: ClassVar[str] = "detail"
    PLAIN_PATH: ClassVar[str] = "/v1/probe"
    OPERATOR_PATH: ClassVar[str] = "/v1/operators/{operator_id}/probe"
    MALFORMED_OPERATOR_ID: ClassVar[str] = "not-a-uuid"
    EXPIRED_S: ClassVar[int] = -60
    DEFAULT_TTL_S: ClassVar[int] = 300
    OTHER_AUDIENCE: ClassVar[str] = "another-audience"

    def path_of(self, operator_id: Union[UUID, str]) -> str:
        return self.OPERATOR_PATH.format(operator_id=operator_id)

    def token_of(
        self,
        stand_in: KeycloakStandIn,
        operator_id: Optional[UUID],
        roles: Optional[List[RoleName]] = None,
        expires_in_s: int = DEFAULT_TTL_S,
        audience: str = AUDIENCE,
    ) -> str:
        granted = [RoleName.MISSION_PLANNER] if roles is None else roles
        return stand_in.mint(claims_for(stand_in.issuer_url, uuid4(), operator_id, granted, audience), expires_in_s)

    def bearer(self, token: str, scheme: Optional[str] = None) -> Dict[str, str]:
        used = self.BEARER if scheme is None else scheme
        return {self.AUTHORIZATION: f"{used} {token}"}

    def assert_logged(self, caplog: pytest.LogCaptureFixture, path: str, refusal: AccessRefusal) -> None:
        messages = [record.getMessage() for record in caplog.records if record.levelno == logging.WARNING]
        assert any(path in message and refusal.value in message for message in messages)

    async def test_a_call_without_a_token_is_refused_and_logged(
        self, client: AsyncClient, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)

        response = await client.get(self.PLAIN_PATH)

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.headers[self.WWW_AUTHENTICATE] == self.BEARER
        assert response.headers[self.CONTENT_TYPE].startswith(self.PROBLEM_JSON)
        body = response.json()
        for key in (self.TYPE_KEY, self.TITLE_KEY, self.STATUS_KEY, self.DETAIL_KEY):
            assert key in body
        assert body[self.STATUS_KEY] == HTTPStatus.UNAUTHORIZED
        self.assert_logged(caplog, self.PLAIN_PATH, AccessRefusal.MISSING_TOKEN)

    async def test_a_call_with_an_expired_token_is_refused_and_logged(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = self.token_of(keycloak_stand_in, uuid4(), expires_in_s=self.EXPIRED_S)

        response = await client.get(self.PLAIN_PATH, headers=self.bearer(token))

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.headers[self.WWW_AUTHENTICATE] == self.BEARER
        self.assert_logged(caplog, self.PLAIN_PATH, AccessRefusal.EXPIRED_TOKEN)

    async def test_another_operators_identifier_is_refused_as_not_found_and_logged(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = self.token_of(keycloak_stand_in, uuid4())
        path = self.path_of(uuid4())

        response = await client.get(path, headers=self.bearer(token))

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.headers[self.CONTENT_TYPE].startswith(self.PROBLEM_JSON)
        self.assert_logged(caplog, path, AccessRefusal.WRONG_OPERATOR)

    async def test_a_malformed_operator_identifier_is_not_found(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = self.token_of(keycloak_stand_in, uuid4())
        path = self.path_of(self.MALFORMED_OPERATOR_ID)

        response = await client.get(path, headers=self.bearer(token))

        assert response.status_code == HTTPStatus.NOT_FOUND
        self.assert_logged(caplog, path, AccessRefusal.WRONG_OPERATOR)

    async def test_the_right_operator_and_role_are_let_through(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        operator_id = uuid4()
        token = self.token_of(keycloak_stand_in, operator_id)

        response = await client.get(self.path_of(operator_id), headers=self.bearer(token))

        assert response.status_code == HTTPStatus.OK

    async def test_a_wrong_role_is_forbidden_and_logged(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        operator_id = uuid4()
        token = self.token_of(keycloak_stand_in, operator_id, [RoleName.PILOT])
        path = self.path_of(operator_id)

        response = await client.get(path, headers=self.bearer(token))

        assert response.status_code == HTTPStatus.FORBIDDEN
        self.assert_logged(caplog, path, AccessRefusal.MISSING_ROLE)

    async def test_a_forged_token_is_refused_as_invalid(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        claims = claims_for(keycloak_stand_in.issuer_url, uuid4(), uuid4(), [RoleName.MISSION_PLANNER])
        token = keycloak_stand_in.forge(claims)

        response = await client.get(self.PLAIN_PATH, headers=self.bearer(token))

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        self.assert_logged(caplog, self.PLAIN_PATH, AccessRefusal.INVALID_TOKEN)

    async def test_a_wrong_audience_is_refused_as_invalid(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = self.token_of(keycloak_stand_in, uuid4(), audience=self.OTHER_AUDIENCE)

        response = await client.get(self.PLAIN_PATH, headers=self.bearer(token))

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        self.assert_logged(caplog, self.PLAIN_PATH, AccessRefusal.INVALID_TOKEN)

    async def test_a_scheme_that_is_not_bearer_counts_as_no_token(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = self.token_of(keycloak_stand_in, uuid4())

        response = await client.get(self.PLAIN_PATH, headers=self.bearer(token, self.BASIC))

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        self.assert_logged(caplog, self.PLAIN_PATH, AccessRefusal.MISSING_TOKEN)

    async def test_the_bearer_scheme_is_case_insensitive(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        token = self.token_of(keycloak_stand_in, uuid4())

        response = await client.get(self.PLAIN_PATH, headers=self.bearer(token, self.BEARER.lower()))

        assert response.status_code == HTTPStatus.OK

    async def test_an_unreachable_issuer_gives_service_unavailable_and_is_logged(
        self,
        unreachable_client: AsyncClient,
        keycloak_stand_in: KeycloakStandIn,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = self.token_of(keycloak_stand_in, uuid4())

        response = await unreachable_client.get(self.PLAIN_PATH, headers=self.bearer(token))

        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        self.assert_logged(caplog, self.PLAIN_PATH, AccessRefusal.IDENTITY_UNAVAILABLE)

    async def test_the_token_never_appears_in_the_logs_or_the_answer(
        self, client: AsyncClient, keycloak_stand_in: KeycloakStandIn, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        claims = claims_for(keycloak_stand_in.issuer_url, uuid4(), uuid4(), [RoleName.MISSION_PLANNER])
        tokens = [
            keycloak_stand_in.forge(claims),
            self.token_of(keycloak_stand_in, uuid4(), expires_in_s=self.EXPIRED_S),
            self.token_of(keycloak_stand_in, uuid4()),
        ]

        for token in tokens:
            response = await client.get(self.path_of(uuid4()), headers=self.bearer(token))
            assert token not in response.text

        for token in tokens:
            assert token not in caplog.text
