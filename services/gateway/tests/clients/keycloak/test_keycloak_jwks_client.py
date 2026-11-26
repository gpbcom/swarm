from __future__ import annotations

# Standard library imports
import asyncio
from typing import ClassVar

# Third-party imports
import jwt
import pytest

# First-party imports
from gateway.clients.keycloak.keycloak_jwks_client import KeycloakJwksClient
from gateway.models.auth.auth_config import AuthConfig
from gateway.models.keycloak.exceptions import SEKeycloakUnknownKeyError, SEKeycloakUnreachableError

from services.gateway.tests.support.keycloak.keycloak_stand_in import KeycloakStandIn  # isort: skip


class TestKeycloakJwksClient:
    UNKNOWN_KEY_ID: ClassVar[str] = "never-served"
    UNREACHABLE_ISSUER: ClassVar[str] = "http://127.0.0.1:1/realms/swarm"
    SHORT_TTL_S: ClassVar[float] = 0.05
    SLEEP_S: ClassVar[float] = 0.3
    KID_FIELD: ClassVar[str] = "kid"

    def served_key_id(self, stand_in: KeycloakStandIn) -> str:
        return str(jwt.get_unverified_header(stand_in.mint({}))[self.KID_FIELD])

    async def test_the_served_key_is_returned_and_fetched_once_for_two_calls(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        client = KeycloakJwksClient(auth_config)
        key_id = self.served_key_id(keycloak_stand_in)
        first = await client.signing_key(key_id)
        second = await client.signing_key(key_id)
        assert first[self.KID_FIELD] == key_id
        assert second == first
        assert keycloak_stand_in.certs_requests == 1

    async def test_a_rotated_key_is_found_with_one_refetch(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        client = KeycloakJwksClient(auth_config)
        await client.signing_key(self.served_key_id(keycloak_stand_in))
        keycloak_stand_in.rotate()
        new_key_id = self.served_key_id(keycloak_stand_in)
        key = await client.signing_key(new_key_id)
        assert key[self.KID_FIELD] == new_key_id
        assert keycloak_stand_in.certs_requests == 2

    async def test_a_key_never_served_is_unknown_after_one_refetch(
        self, keycloak_stand_in: KeycloakStandIn, auth_config: AuthConfig
    ) -> None:
        client = KeycloakJwksClient(auth_config)
        await client.signing_key(self.served_key_id(keycloak_stand_in))
        with pytest.raises(SEKeycloakUnknownKeyError):
            await client.signing_key(self.UNKNOWN_KEY_ID)
        assert keycloak_stand_in.certs_requests == 2

    async def test_the_keys_are_fetched_again_after_the_cache_ttl(self, keycloak_stand_in: KeycloakStandIn) -> None:
        config = AuthConfig(issuer_url=keycloak_stand_in.issuer_url, jwks_cache_ttl_s=self.SHORT_TTL_S)
        client = KeycloakJwksClient(config)
        key_id = self.served_key_id(keycloak_stand_in)
        await client.signing_key(key_id)
        await asyncio.sleep(self.SLEEP_S)
        await client.signing_key(key_id)
        assert keycloak_stand_in.certs_requests == 2

    async def test_an_unreachable_issuer_raises_unreachable(self) -> None:
        client = KeycloakJwksClient(AuthConfig(issuer_url=self.UNREACHABLE_ISSUER))
        with pytest.raises(SEKeycloakUnreachableError):
            await client.signing_key(self.UNKNOWN_KEY_ID)
