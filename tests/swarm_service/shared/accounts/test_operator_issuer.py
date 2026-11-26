from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, cast

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from swarm_nats.models.accounts.exceptions import SEIssuedOperatorInvalidName
from swarm_nats.models.accounts.issued_operator import IssuedOperator
from swarm_nats.models.enums import NatsClaimType
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_nats.service.accounts.nkey_factory import NkeyFactory
from swarm_nats.service.accounts.operator_issuer import OperatorIssuer


class TestOperatorIssuer:
    OPERATOR_NAME: ClassVar[str] = "swarm-operator"
    SYSTEM_ACCOUNT_NAME: ClassVar[str] = "SYS"
    SUB_KEY: ClassVar[str] = "sub"
    ISS_KEY: ClassVar[str] = "iss"
    NAME_KEY: ClassVar[str] = "name"
    NATS_KEY: ClassVar[str] = "nats"
    TYPE_KEY: ClassVar[str] = "type"
    VERSION_KEY: ClassVar[str] = "version"
    SYSTEM_ACCOUNT_KEY: ClassVar[str] = "system_account"
    NATS_VERSION: ClassVar[int] = 2

    def issuer(self) -> OperatorIssuer:
        return OperatorIssuer(NkeyFactory(), NatsJwtSigner(), logger=None)

    def claims(self, token: str) -> Dict[str, JsonValue]:
        return NatsJwtSigner().decode(token)

    def nats(self, claims: Dict[str, JsonValue]) -> Dict[str, JsonValue]:
        return cast(Dict[str, JsonValue], claims[self.NATS_KEY])

    def test_the_operator_jwt_is_self_signed(self) -> None:
        operator = self.issuer().issue(self.OPERATOR_NAME)
        claims = self.claims(operator.jwt)
        assert claims[self.SUB_KEY] == operator.public_key
        assert claims[self.ISS_KEY] == operator.public_key

    def test_the_operator_jwt_carries_its_name(self) -> None:
        operator = self.issuer().issue(self.OPERATOR_NAME)
        assert self.claims(operator.jwt)[self.NAME_KEY] == self.OPERATOR_NAME

    def test_the_operator_jwt_is_a_version_2_operator_claim(self) -> None:
        operator = self.issuer().issue(self.OPERATOR_NAME)
        nats = self.nats(self.claims(operator.jwt))
        assert nats[self.TYPE_KEY] == NatsClaimType.OPERATOR.value
        assert nats[self.VERSION_KEY] == self.NATS_VERSION

    def test_the_operator_jwt_names_its_system_account(self) -> None:
        operator = self.issuer().issue(self.OPERATOR_NAME)
        nats = self.nats(self.claims(operator.jwt))
        assert nats[self.SYSTEM_ACCOUNT_KEY] == operator.system_account.public_key

    def test_the_system_account_jwt_is_signed_by_the_operator(self) -> None:
        operator = self.issuer().issue(self.OPERATOR_NAME)
        claims = self.claims(operator.system_account.jwt)
        assert claims[self.ISS_KEY] == operator.public_key
        assert claims[self.SUB_KEY] == operator.system_account.public_key

    def test_the_system_account_is_named_sys_and_is_an_account(self) -> None:
        operator = self.issuer().issue(self.OPERATOR_NAME)
        claims = self.claims(operator.system_account.jwt)
        assert claims[self.NAME_KEY] == self.SYSTEM_ACCOUNT_NAME
        assert self.nats(claims)[self.TYPE_KEY] == NatsClaimType.ACCOUNT.value

    def test_the_result_is_an_issued_operator(self) -> None:
        assert isinstance(self.issuer().issue(self.OPERATOR_NAME), IssuedOperator)

    def test_two_calls_give_different_keys(self) -> None:
        issuer = self.issuer()
        first = issuer.issue(self.OPERATOR_NAME)
        second = issuer.issue(self.OPERATOR_NAME)
        assert first.public_key != second.public_key
        assert first.system_account.public_key != second.system_account.public_key

    def test_an_empty_name_is_refused(self) -> None:
        with pytest.raises(SEIssuedOperatorInvalidName):
            self.issuer().issue("")
