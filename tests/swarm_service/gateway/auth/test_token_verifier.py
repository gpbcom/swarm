from __future__ import annotations

# Standard library imports
import logging
from typing import ClassVar, Dict, List, Optional
from uuid import UUID

# Third-party imports
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import JsonValue

# First-party imports
from gateway.clients.keycloak.keycloak_jwks_client import KeycloakJwksClient  # isort: skip
from gateway.models.access.exceptions import (  # isort: skip
    SEAccessExpiredTokenError,
    SEAccessInvalidTokenError,
    SEAccessMissingTokenError,
)
from gateway.models.auth.auth_config import AuthConfig  # isort: skip
from gateway.models.auth.caller import Caller  # isort: skip
from gateway.models.enums import TokenClaim  # isort: skip
from gateway.models.keycloak.exceptions import SEKeycloakUnreachableError  # isort: skip
from gateway.service.auth.token_verifier import TokenVerifier  # isort: skip
from swarm_models.people.enums import RoleName  # isort: skip
from services.gateway.tests.support.keycloak.helpers import AUDIENCE, claims_for  # isort: skip
from services.gateway.tests.support.keycloak.keycloak_stand_in import KeycloakStandIn  # isort: skip


class TestTokenVerifier:
    PERSON_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62")
    OPERATOR_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    NOT_A_UUID: ClassVar[str] = "not-a-uuid"
    OTHER_ROLE: ClassVar[str] = "offline_access"
    WRONG_ISSUER: ClassVar[str] = "http://127.0.0.1:1/realms/other"
    WRONG_AUDIENCE: ClassVar[str] = "another-audience"
    SYMMETRIC_SECRET: ClassVar[str] = "a-symmetric-secret-of-at-least-32-bytes"
    MALFORMED_TOKEN: ClassVar[str] = "this.is.not-a-token"
    RS256: ClassVar[str] = "RS256"
    KID_HEADER: ClassVar[str] = "kid"
    EXPIRED_S: ClassVar[int] = -120
    LEEWAY_S: ClassVar[float] = 60.0
    JUST_EXPIRED_S: ClassVar[int] = -30
    UNREACHABLE_ISSUER: ClassVar[str] = "http://127.0.0.1:1/realms/swarm"
    SHORT_TIMEOUT_S: ClassVar[float] = 1.0

    def a_verifier(self, config: AuthConfig) -> TokenVerifier:
        return TokenVerifier(config, KeycloakJwksClient(config))

    def claims(self, stand_in: KeycloakStandIn, roles: Optional[List[RoleName]] = None) -> Dict[str, JsonValue]:
        return claims_for(
            stand_in.issuer_url,
            self.PERSON_ID,
            self.OPERATOR_ID,
            roles if roles is not None else [RoleName.PILOT],
        )

    def error_records(self, caplog: pytest.LogCaptureFixture) -> List[logging.LogRecord]:
        return [record for record in caplog.records if record.levelno >= logging.ERROR]

    async def test_a_valid_token_gives_the_caller(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        token = keycloak_stand_in.mint(self.claims(keycloak_stand_in, [RoleName.PILOT, RoleName.MISSION_PLANNER]))

        caller = await self.a_verifier(auth_config).verify(token)

        assert caller == Caller(
            person_id=self.PERSON_ID,
            operator_id=self.OPERATOR_ID,
            roles=[RoleName.PILOT, RoleName.MISSION_PLANNER],
        )

    async def test_other_keycloak_roles_are_ignored(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        claims = self.claims(keycloak_stand_in)
        claims[TokenClaim.REALM_ACCESS.value] = {TokenClaim.ROLES.value: [RoleName.PILOT.value, self.OTHER_ROLE]}

        caller = await self.a_verifier(auth_config).verify(keycloak_stand_in.mint(claims))

        assert caller.roles == [RoleName.PILOT]

    async def test_a_swarm_administrator_has_no_operator(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        claims = claims_for(keycloak_stand_in.issuer_url, self.PERSON_ID, None, [RoleName.SWARM_ADMINISTRATOR])

        caller = await self.a_verifier(auth_config).verify(keycloak_stand_in.mint(claims))

        assert caller.operator_id is None
        assert caller.roles == [RoleName.SWARM_ADMINISTRATOR]

    @pytest.mark.parametrize("token", [None, "", "   "])
    async def test_a_missing_or_blank_token_is_refused_and_logged(
        self, auth_config: AuthConfig, caplog: pytest.LogCaptureFixture, token: Optional[str]
    ) -> None:
        caplog.set_level(logging.DEBUG)

        with pytest.raises(SEAccessMissingTokenError):
            await self.a_verifier(auth_config).verify(token)

        assert self.error_records(caplog)

    async def test_an_expired_token_is_refused_and_logged(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = keycloak_stand_in.mint(self.claims(keycloak_stand_in), expires_in_s=self.EXPIRED_S)

        with pytest.raises(SEAccessExpiredTokenError):
            await self.a_verifier(auth_config).verify(token)

        assert self.error_records(caplog)
        assert token not in caplog.text

    async def test_an_expiry_inside_the_leeway_is_accepted(self, keycloak_stand_in: KeycloakStandIn) -> None:
        config = AuthConfig(issuer_url=keycloak_stand_in.issuer_url, audience=AUDIENCE, leeway_s=self.LEEWAY_S)
        token = keycloak_stand_in.mint(self.claims(keycloak_stand_in), expires_in_s=self.JUST_EXPIRED_S)

        caller = await self.a_verifier(config).verify(token)

        assert caller.person_id == self.PERSON_ID

    async def test_an_expiry_beyond_the_leeway_is_refused(self, keycloak_stand_in: KeycloakStandIn) -> None:
        config = AuthConfig(issuer_url=keycloak_stand_in.issuer_url, audience=AUDIENCE, leeway_s=self.LEEWAY_S)
        token = keycloak_stand_in.mint(self.claims(keycloak_stand_in), expires_in_s=self.EXPIRED_S)

        with pytest.raises(SEAccessExpiredTokenError):
            await self.a_verifier(config).verify(token)

    async def test_a_malformed_token_is_refused_and_logged(
        self, auth_config: AuthConfig, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(self.MALFORMED_TOKEN)

        assert self.error_records(caplog)
        assert self.MALFORMED_TOKEN not in caplog.text

    async def test_a_token_signed_by_another_key_is_refused_and_logged(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.DEBUG)
        token = keycloak_stand_in.forge(self.claims(keycloak_stand_in))

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(token)

        assert self.error_records(caplog)
        assert token not in caplog.text

    async def test_a_token_with_a_bad_signature_is_refused(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        token = keycloak_stand_in.mint(self.claims(keycloak_stand_in))
        header, payload, signature = token.split(".")
        tampered = ".".join([header, payload, signature[::-1]])

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(tampered)

    async def test_a_token_without_a_kid_is_refused(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        token = jwt.encode(self.claims(keycloak_stand_in), key, algorithm=self.RS256)

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(token)

    async def test_a_token_with_a_kid_the_keys_do_not_hold_is_refused_after_a_rotation(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        token = keycloak_stand_in.mint(self.claims(keycloak_stand_in))
        keycloak_stand_in.rotate()

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(token)

    @pytest.mark.parametrize("algorithm", ["HS256", "none"])
    async def test_an_algorithm_other_than_rs256_is_refused(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig, algorithm: str
    ) -> None:
        minted = keycloak_stand_in.mint(self.claims(keycloak_stand_in))
        kid = jwt.get_unverified_header(minted)[self.KID_HEADER]
        secret: Optional[str] = None if algorithm == "none" else self.SYMMETRIC_SECRET
        token = jwt.encode(self.claims(keycloak_stand_in), secret, algorithm=algorithm, headers={self.KID_HEADER: kid})

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(token)

    @pytest.mark.parametrize(
        ("claim", "value"),
        [
            (TokenClaim.ISSUER, WRONG_ISSUER),
            (TokenClaim.AUDIENCE, WRONG_AUDIENCE),
            (TokenClaim.SUBJECT, NOT_A_UUID),
            (TokenClaim.OPERATOR_ID, NOT_A_UUID),
        ],
    )
    async def test_a_wrong_claim_is_refused_and_logged(
        self,
        keycloak_stand_in: KeycloakStandIn,
        auth_config: AuthConfig,
        caplog: pytest.LogCaptureFixture,
        claim: TokenClaim,
        value: str,
    ) -> None:
        caplog.set_level(logging.DEBUG)
        claims = self.claims(keycloak_stand_in)
        claims[claim.value] = value
        token = keycloak_stand_in.mint(claims)

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(token)

        assert self.error_records(caplog)
        assert token not in caplog.text

    async def test_a_token_without_a_subject_is_refused(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        claims = self.claims(keycloak_stand_in)
        del claims[TokenClaim.SUBJECT.value]

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(keycloak_stand_in.mint(claims))

    @pytest.mark.parametrize(
        ("roles", "has_operator"),
        [([RoleName.PILOT], False), ([RoleName.SWARM_ADMINISTRATOR], True)],
    )
    async def test_claims_that_the_caller_refuses_are_an_invalid_token(
        self,
        keycloak_stand_in: KeycloakStandIn,
        auth_config: AuthConfig,
        roles: List[RoleName],
        has_operator: bool,
    ) -> None:
        operator_id = self.OPERATOR_ID if has_operator else None
        claims = claims_for(keycloak_stand_in.issuer_url, self.PERSON_ID, operator_id, roles)

        with pytest.raises(SEAccessInvalidTokenError):
            await self.a_verifier(auth_config).verify(keycloak_stand_in.mint(claims))

    async def test_an_unreachable_keycloak_is_not_turned_into_a_refusal(
        self, keycloak_stand_in: KeycloakStandIn
    ) -> None:
        config = AuthConfig(
            issuer_url=self.UNREACHABLE_ISSUER, audience=AUDIENCE, request_timeout_s=self.SHORT_TIMEOUT_S
        )
        token = keycloak_stand_in.mint(self.claims(keycloak_stand_in))

        with pytest.raises(SEKeycloakUnreachableError):
            await self.a_verifier(config).verify(token)
