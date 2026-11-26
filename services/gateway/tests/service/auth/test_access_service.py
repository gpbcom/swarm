from __future__ import annotations

# Standard library imports
import logging
from typing import ClassVar, List, Optional
from uuid import UUID, uuid4

# Third-party imports
import pytest

# First-party imports
from gateway.models.access.exceptions import (
    SEAccessExpiredTokenError,
    SEAccessInvalidTokenError,
    SEAccessMissingRoleError,
    SEAccessMissingTokenError,
    SEAccessWrongOperatorError,
)
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.keycloak.exceptions import SEKeycloakUnreachableError
from gateway.service.auth.access_service import AccessService

from services.gateway.tests.support.keycloak.helpers import claims_for  # isort: skip
from services.gateway.tests.support.keycloak.keycloak_stand_in import KeycloakStandIn  # isort: skip
from swarm_models.people.enums import RoleName


class TestAccessService:
    OPERATOR_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OTHER_OPERATOR_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    UNREACHABLE_ISSUER: ClassVar[str] = "http://127.0.0.1:1/realms/swarm"

    def token_for(
        self,
        stand_in: KeycloakStandIn,
        operator_id: Optional[UUID],
        roles: List[RoleName],
        person_id: Optional[UUID] = None,
        expires_in_s: int = 300,
    ) -> str:
        claims = claims_for(stand_in.issuer_url, person_id or uuid4(), operator_id, roles)
        return stand_in.mint(claims, expires_in_s=expires_in_s)

    async def test_a_valid_token_with_the_right_role_and_operator_returns_the_caller(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        person_id = uuid4()
        token = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT], person_id)
        service = AccessService.from_config(auth_config)

        caller = await service.authorise(token, [RoleName.PILOT, RoleName.MISSION_PLANNER], self.OPERATOR_ID)

        assert caller.person_id == person_id
        assert caller.operator_id == self.OPERATOR_ID
        assert list(caller.roles) == [RoleName.PILOT]

    async def test_no_operator_to_check_verifies_the_role_only(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        token = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT])
        service = AccessService.from_config(auth_config)

        caller = await service.authorise(token, [RoleName.PILOT], None)

        assert caller.operator_id == self.OPERATOR_ID

    @pytest.mark.parametrize("token", [None, "", "   "])
    async def test_no_token_is_refused(self, auth_config: AuthConfig, token: Optional[str]) -> None:
        service = AccessService.from_config(auth_config)

        with pytest.raises(SEAccessMissingTokenError):
            await service.authorise(token, [RoleName.PILOT], self.OPERATOR_ID)

    async def test_an_expired_token_is_refused(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        token = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT], expires_in_s=-3600)
        service = AccessService.from_config(auth_config)

        with pytest.raises(SEAccessExpiredTokenError):
            await service.authorise(token, [RoleName.PILOT], self.OPERATOR_ID)

    async def test_another_operators_id_is_refused(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        token = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT])
        service = AccessService.from_config(auth_config)

        with pytest.raises(SEAccessWrongOperatorError):
            await service.authorise(token, [RoleName.PILOT], self.OTHER_OPERATOR_ID)

    async def test_a_missing_role_is_refused(self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig) -> None:
        token = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT])
        service = AccessService.from_config(auth_config)

        with pytest.raises(SEAccessMissingRoleError):
            await service.authorise(token, [RoleName.MISSION_PLANNER], self.OPERATOR_ID)

    async def test_an_invalid_token_is_refused_before_any_role_check(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        claims = claims_for(keycloak_stand_in.issuer_url, uuid4(), self.OPERATOR_ID, [RoleName.PILOT])
        forged = keycloak_stand_in.forge(claims)
        service = AccessService.from_config(auth_config)

        with pytest.raises(SEAccessInvalidTokenError):
            await service.authorise(forged, [RoleName.MISSION_PLANNER], self.OTHER_OPERATOR_ID)

    async def test_an_unreachable_keycloak_is_reported(self, keycloak_stand_in: KeycloakStandIn) -> None:
        token = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT])
        config = AuthConfig(issuer_url=self.UNREACHABLE_ISSUER)
        service = AccessService.from_config(config)

        with pytest.raises(SEKeycloakUnreachableError):
            await service.authorise(token, [RoleName.PILOT], self.OPERATOR_ID)

    async def test_the_token_never_appears_in_the_logs(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig, caplog: pytest.LogCaptureFixture
    ) -> None:
        good = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT])
        expired = self.token_for(keycloak_stand_in, self.OPERATOR_ID, [RoleName.PILOT], expires_in_s=-3600)
        service = AccessService.from_config(auth_config)

        with caplog.at_level(logging.DEBUG):
            await service.authorise(good, [RoleName.PILOT], self.OPERATOR_ID)
            with pytest.raises(SEAccessExpiredTokenError):
                await service.authorise(expired, [RoleName.PILOT], self.OPERATOR_ID)
            with pytest.raises(SEAccessMissingRoleError):
                await service.authorise(good, [RoleName.MISSION_PLANNER], self.OPERATOR_ID)

        assert good not in caplog.text
        assert expired not in caplog.text
