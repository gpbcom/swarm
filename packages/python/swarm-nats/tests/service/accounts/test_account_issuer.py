from __future__ import annotations

from typing import ClassVar, Dict, List, cast
from uuid import UUID

import pytest
from pydantic import JsonValue

from swarm_nats.models.accounts.exceptions import SENatsJwtInvalidError
from swarm_nats.models.accounts.issued_account import IssuedAccount
from swarm_nats.models.accounts.issued_credential import IssuedCredential
from swarm_nats.models.accounts.issued_operator import IssuedOperator
from swarm_nats.models.enums import CredentialKind, NatsClaimType
from swarm_nats.service.accounts.account_issuer import AccountIssuer
from swarm_nats.service.accounts.credential_issuer import CredentialIssuer
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_nats.service.accounts.nkey_factory import NkeyFactory
from swarm_nats.service.accounts.operator_issuer import OperatorIssuer


class TestAccountIssuer:
    OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7b")
    OTHER_OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7c")
    OPERATOR_NAME: ClassVar[str] = "swarm-operator"
    EDGE_NAME: ClassVar[str] = "edge-one"
    SUB_KEY: ClassVar[str] = "sub"
    ISS_KEY: ClassVar[str] = "iss"
    IAT_KEY: ClassVar[str] = "iat"
    NAME_KEY: ClassVar[str] = "name"
    NATS_KEY: ClassVar[str] = "nats"
    TYPE_KEY: ClassVar[str] = "type"
    VERSION_KEY: ClassVar[str] = "version"
    LIMITS_KEY: ClassVar[str] = "limits"
    REVOCATIONS_KEY: ClassVar[str] = "revocations"
    LIMIT_KEYS: ClassVar[List[str]] = ["mem_storage", "disk_storage", "conn", "leaf"]
    NATS_VERSION: ClassVar[int] = 2
    UNLIMITED: ClassVar[int] = -1

    def issuer(self) -> AccountIssuer:
        return AccountIssuer(NkeyFactory(), NatsJwtSigner(), logger=None)

    def operator(self) -> IssuedOperator:
        return OperatorIssuer(NkeyFactory(), NatsJwtSigner(), logger=None).issue(self.OPERATOR_NAME)

    def user(self, account: IssuedAccount) -> IssuedCredential:
        return CredentialIssuer(NkeyFactory(), NatsJwtSigner(), logger=None).issue(
            account, self.OPERATOR_ID, CredentialKind.EDGE, self.EDGE_NAME
        )

    def claims(self, token: str) -> Dict[str, JsonValue]:
        return NatsJwtSigner().decode(token)

    def nats(self, token: str) -> Dict[str, JsonValue]:
        return cast(Dict[str, JsonValue], self.claims(token)[self.NATS_KEY])

    def revocations(self, token: str) -> Dict[str, JsonValue]:
        return cast(Dict[str, JsonValue], self.nats(token).get(self.REVOCATIONS_KEY, {}))

    def test_the_account_is_named_after_the_operator_id(self) -> None:
        account = self.issuer().issue(self.operator(), self.OPERATOR_ID)
        assert isinstance(account, IssuedAccount)
        assert account.name == str(self.OPERATOR_ID)
        assert self.claims(account.jwt)[self.NAME_KEY] == str(self.OPERATOR_ID)

    def test_the_account_jwt_is_signed_by_the_operator(self) -> None:
        operator = self.operator()
        account = self.issuer().issue(operator, self.OPERATOR_ID)
        claims = self.claims(account.jwt)
        assert claims[self.ISS_KEY] == operator.public_key
        assert claims[self.SUB_KEY] == account.public_key

    def test_the_account_jwt_is_a_version_2_account_claim(self) -> None:
        account = self.issuer().issue(self.operator(), self.OPERATOR_ID)
        nats = self.nats(account.jwt)
        assert nats[self.TYPE_KEY] == NatsClaimType.ACCOUNT.value
        assert nats[self.VERSION_KEY] == self.NATS_VERSION

    @pytest.mark.parametrize("limit", LIMIT_KEYS)
    def test_jetstream_is_enabled_without_a_limit(self, limit: str) -> None:
        account = self.issuer().issue(self.operator(), self.OPERATOR_ID)
        limits = cast(Dict[str, JsonValue], self.nats(account.jwt)[self.LIMITS_KEY])
        assert limits[limit] == self.UNLIMITED

    def test_a_new_account_has_no_revocations(self) -> None:
        account = self.issuer().issue(self.operator(), self.OPERATOR_ID)
        assert not self.revocations(account.jwt)

    def test_two_operators_get_different_account_keys(self) -> None:
        operator = self.operator()
        issuer = self.issuer()
        first = issuer.issue(operator, self.OPERATOR_ID)
        second = issuer.issue(operator, self.OTHER_OPERATOR_ID)
        assert first.public_key != second.public_key
        assert second.name == str(self.OTHER_OPERATOR_ID)

    def test_revoking_a_user_keeps_the_account_keys(self) -> None:
        operator = self.operator()
        issuer = self.issuer()
        account = issuer.issue(operator, self.OPERATOR_ID)
        revoked = issuer.revoke(operator, account, [self.user(account).public_key])
        assert isinstance(revoked, IssuedAccount)
        assert revoked.public_key == account.public_key
        assert revoked.seed.get_secret_value() == account.seed.get_secret_value()
        assert revoked.jwt != account.jwt

    def test_a_revocation_is_dated_no_earlier_than_the_user_jwt(self) -> None:
        operator = self.operator()
        issuer = self.issuer()
        account = issuer.issue(operator, self.OPERATOR_ID)
        credential = self.user(account)
        revoked = issuer.revoke(operator, account, [credential.public_key])
        time = self.revocations(revoked.jwt)[credential.public_key]
        issued_at = self.claims(credential.jwt)[self.IAT_KEY]
        assert isinstance(time, int)
        assert isinstance(issued_at, int)
        assert time >= issued_at

    def test_revoking_a_second_key_keeps_the_first_one(self) -> None:
        operator = self.operator()
        issuer = self.issuer()
        account = issuer.issue(operator, self.OPERATOR_ID)
        first = self.user(account).public_key
        second = self.user(account).public_key
        once = issuer.revoke(operator, account, [first])
        twice = issuer.revoke(operator, once, [second])
        assert set(self.revocations(twice.jwt)) == {first, second}

    def test_revoking_with_an_operator_that_did_not_sign_the_account_is_refused(self) -> None:
        issuer = self.issuer()
        account = issuer.issue(self.operator(), self.OPERATOR_ID)
        with pytest.raises(SENatsJwtInvalidError):
            issuer.revoke(self.operator(), account, [self.user(account).public_key])
