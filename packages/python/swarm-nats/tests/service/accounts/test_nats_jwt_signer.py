from __future__ import annotations

import base64
import json
import time
from typing import ClassVar, Dict

import pytest
from nkeys import KeyPair
from pydantic import JsonValue

# First-party imports
from swarm_nats.models.accounts.exceptions import SENatsJwtInvalidError
from swarm_nats.models.enums import NatsClaimType
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_nats.service.accounts.nkey_factory import NkeyFactory


class TestNatsJwtSigner:
    SUB_KEY: ClassVar[str] = "sub"
    NAME_KEY: ClassVar[str] = "name"
    NATS_KEY: ClassVar[str] = "nats"
    PUB_KEY: ClassVar[str] = "pub"
    ALLOW_KEY: ClassVar[str] = "allow"
    ISS_KEY: ClassVar[str] = "iss"
    IAT_KEY: ClassVar[str] = "iat"
    JTI_KEY: ClassVar[str] = "jti"
    TYP_KEY: ClassVar[str] = "typ"
    ALG_KEY: ClassVar[str] = "alg"
    TYP_VALUE: ClassVar[str] = "JWT"
    ALG_VALUE: ClassVar[str] = "ed25519-nkey"
    SEPARATOR: ClassVar[str] = "."
    ENCODING: ClassVar[str] = "utf-8"
    IAT_TOLERANCE_S: ClassVar[int] = 5

    def a_pair(self, kind: NatsClaimType = NatsClaimType.ACCOUNT) -> KeyPair:
        return NkeyFactory().create(kind)

    def some_claims(self) -> Dict[str, JsonValue]:
        return {
            self.SUB_KEY: NkeyFactory().public_key(self.a_pair(NatsClaimType.USER)),
            self.NAME_KEY: "edge-1",
            self.NATS_KEY: {self.PUB_KEY: {self.ALLOW_KEY: ["drone.>"]}},
        }

    def signed(self, issuer: KeyPair) -> str:
        return NatsJwtSigner().sign(self.some_claims(), issuer)

    def b64decode(self, part: str) -> bytes:
        return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))

    def b64encode(self, raw: bytes) -> str:
        return base64.urlsafe_b64encode(raw).decode(self.ENCODING).rstrip("=")

    def test_the_header_is_an_ed25519_nkey_jwt(self) -> None:
        token = self.signed(self.a_pair())
        header = json.loads(self.b64decode(token.split(self.SEPARATOR)[0]))
        assert header == {self.TYP_KEY: self.TYP_VALUE, self.ALG_KEY: self.ALG_VALUE}

    def test_the_claims_round_trip(self) -> None:
        claims = self.some_claims()
        decoded = NatsJwtSigner().decode(NatsJwtSigner().sign(claims, self.a_pair()))
        assert decoded[self.SUB_KEY] == claims[self.SUB_KEY]
        assert decoded[self.NAME_KEY] == claims[self.NAME_KEY]
        assert decoded[self.NATS_KEY] == claims[self.NATS_KEY]

    def test_the_issuer_is_the_public_key_of_the_signing_pair(self) -> None:
        issuer = self.a_pair()
        decoded = NatsJwtSigner().decode(self.signed(issuer))
        assert decoded[self.ISS_KEY] == NkeyFactory().public_key(issuer)

    def test_the_issue_time_is_the_current_time_in_whole_seconds(self) -> None:
        decoded = NatsJwtSigner().decode(self.signed(self.a_pair()))
        iat = decoded[self.IAT_KEY]
        assert isinstance(iat, int)
        assert abs(iat - time.time()) <= self.IAT_TOLERANCE_S

    def test_the_identifier_is_a_non_empty_string(self) -> None:
        decoded = NatsJwtSigner().decode(self.signed(self.a_pair()))
        jti = decoded[self.JTI_KEY]
        assert isinstance(jti, str)
        assert jti

    def test_a_payload_changed_by_one_character_is_refused(self) -> None:
        header, payload, signature = self.signed(self.a_pair()).split(self.SEPARATOR)
        index = len(payload) // 2
        changed = "A" if payload[index] != "A" else "B"
        tampered = self.SEPARATOR.join([header, payload[:index] + changed + payload[index + 1 :], signature])
        with pytest.raises(SENatsJwtInvalidError):
            NatsJwtSigner().decode(tampered)

    def test_a_replaced_issuer_is_refused(self) -> None:
        header, payload, signature = self.signed(self.a_pair()).split(self.SEPARATOR)
        claims = json.loads(self.b64decode(payload))
        claims[self.ISS_KEY] = NkeyFactory().public_key(self.a_pair())
        forged = self.b64encode(json.dumps(claims).encode(self.ENCODING))
        with pytest.raises(SENatsJwtInvalidError):
            NatsJwtSigner().decode(self.SEPARATOR.join([header, forged, signature]))

    @pytest.mark.parametrize("token", ["", "abc", "a.b", "a.b.c.d"])
    def test_a_token_without_three_parts_is_refused(self, token: str) -> None:
        with pytest.raises(SENatsJwtInvalidError):
            NatsJwtSigner().decode(token)
