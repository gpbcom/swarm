from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Set, Tuple, cast
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from swarm_nats.models.accounts.exceptions import (
    SECredentialIssuerAccountMismatchError,
    SECredentialIssuerInvalidKindError,
)
from swarm_nats.models.accounts.issued_account import IssuedAccount
from swarm_nats.models.accounts.issued_credential import IssuedCredential
from swarm_nats.models.accounts.issued_operator import IssuedOperator
from swarm_nats.models.enums import CredentialKind, NatsClaimType
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects
from swarm_nats.service.accounts.account_issuer import AccountIssuer
from swarm_nats.service.accounts.credential_issuer import CredentialIssuer
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_nats.service.accounts.nkey_factory import NkeyFactory
from swarm_nats.service.accounts.operator_issuer import OperatorIssuer


class TestCredentialIssuer:
    OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7b")
    OTHER_OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7c")
    OPERATOR_NAME: ClassVar[str] = "swarm-operator"
    CREDENTIAL_NAME: ClassVar[str] = "worker-one"
    SUB_KEY: ClassVar[str] = "sub"
    ISS_KEY: ClassVar[str] = "iss"
    NAME_KEY: ClassVar[str] = "name"
    NATS_KEY: ClassVar[str] = "nats"
    TYPE_KEY: ClassVar[str] = "type"
    VERSION_KEY: ClassVar[str] = "version"
    PUB_KEY: ClassVar[str] = "pub"
    SUBSCRIBE_KEY: ClassVar[str] = "sub"
    ALLOW_KEY: ClassVar[str] = "allow"
    TAGS_KEY: ClassVar[str] = "tags"
    NATS_VERSION: ClassVar[int] = 2
    WILDCARD_ALL: ClassVar[str] = ">"
    OPERATOR_PREFIX: ClassVar[str] = "op."
    INBOX_SUBJECT: ClassVar[str] = "_INBOX.>"
    JETSTREAM_SUBJECT: ClassVar[str] = "$JS.>"
    KV_SUBJECT: ClassVar[str] = "$KV.>"
    SYSTEM_TAG: ClassVar[str] = "system"
    JWT_BEGIN: ClassVar[str] = "-----BEGIN NATS USER JWT-----"
    JWT_END: ClassVar[str] = "------END NATS USER JWT------"
    SEED_BEGIN: ClassVar[str] = "-----BEGIN USER NKEY SEED-----"
    SEED_END: ClassVar[str] = "------END USER NKEY SEED------"
    PERMISSIONS: ClassVar[List[str]] = [PUB_KEY, SUBSCRIBE_KEY]
    ISSUED_KINDS: ClassVar[List[CredentialKind]] = [
        CredentialKind.SERVICE,
        CredentialKind.EDGE,
        CredentialKind.SIMULATED,
    ]

    def issuer(self) -> CredentialIssuer:
        return CredentialIssuer(NkeyFactory(), NatsJwtSigner(), logger=None)

    def operator(self) -> IssuedOperator:
        return OperatorIssuer(NkeyFactory(), NatsJwtSigner(), logger=None).issue(self.OPERATOR_NAME)

    def account(self, operator: IssuedOperator) -> IssuedAccount:
        return AccountIssuer(NkeyFactory(), NatsJwtSigner(), logger=None).issue(operator, self.OPERATOR_ID)

    def claims(self, token: str) -> Dict[str, JsonValue]:
        return NatsJwtSigner().decode(token)

    def nats(self, token: str) -> Dict[str, JsonValue]:
        return cast(Dict[str, JsonValue], self.claims(token)[self.NATS_KEY])

    def allowed(self, token: str, permission: str) -> List[str]:
        section = cast(Dict[str, JsonValue], self.nats(token)[permission])
        return cast(List[str], section[self.ALLOW_KEY])

    def issue(self, kind: CredentialKind) -> Tuple[IssuedAccount, IssuedCredential]:
        account = self.account(self.operator())
        return account, self.issuer().issue(account, self.OPERATOR_ID, kind, self.CREDENTIAL_NAME)

    @pytest.mark.parametrize("kind", ISSUED_KINDS)
    def test_the_credential_holds_what_it_was_given(self, kind: CredentialKind) -> None:
        _, credential = self.issue(kind)
        assert isinstance(credential, IssuedCredential)
        assert credential.operator_id == self.OPERATOR_ID
        assert credential.kind == kind
        assert credential.name == self.CREDENTIAL_NAME

    @pytest.mark.parametrize("kind", ISSUED_KINDS)
    def test_the_jwt_is_signed_by_the_account(self, kind: CredentialKind) -> None:
        account, credential = self.issue(kind)
        claims = self.claims(credential.jwt)
        assert claims[self.ISS_KEY] == account.public_key
        assert claims[self.SUB_KEY] == credential.public_key

    @pytest.mark.parametrize("kind", ISSUED_KINDS)
    def test_the_jwt_is_a_version_2_user_claim(self, kind: CredentialKind) -> None:
        _, credential = self.issue(kind)
        assert self.claims(credential.jwt)[self.NAME_KEY] == self.CREDENTIAL_NAME
        nats = self.nats(credential.jwt)
        assert nats[self.TYPE_KEY] == NatsClaimType.USER.value
        assert nats[self.VERSION_KEY] == self.NATS_VERSION

    @pytest.mark.parametrize("permission", PERMISSIONS)
    @pytest.mark.parametrize("kind", ISSUED_KINDS)
    def test_the_credential_may_only_use_its_operator_subjects_and_the_mechanism_subjects(
        self, kind: CredentialKind, permission: str
    ) -> None:
        _, credential = self.issue(kind)
        expected: Set[str] = {OperatorSubjects(operator_id=self.OPERATOR_ID).all()} | set(
            CredentialIssuer.MECHANISM_SUBJECTS
        )
        assert set(self.allowed(credential.jwt, permission)) == expected

    def test_the_mechanism_subjects_cover_inboxes_and_jetstream(self) -> None:
        assert {self.INBOX_SUBJECT, self.JETSTREAM_SUBJECT, self.KV_SUBJECT} <= set(CredentialIssuer.MECHANISM_SUBJECTS)

    @pytest.mark.parametrize("permission", PERMISSIONS)
    @pytest.mark.parametrize("kind", ISSUED_KINDS)
    def test_no_allowed_subject_is_a_wildcard_or_another_operators(self, kind: CredentialKind, permission: str) -> None:
        _, credential = self.issue(kind)
        own = OperatorSubjects(operator_id=self.OPERATOR_ID).all()
        for subject in self.allowed(credential.jwt, permission):
            assert subject != self.WILDCARD_ALL
            if subject.startswith(self.OPERATOR_PREFIX):
                assert subject == own

    @pytest.mark.parametrize("kind", ISSUED_KINDS)
    def test_the_credential_is_tagged_with_its_kind(self, kind: CredentialKind) -> None:
        _, credential = self.issue(kind)
        assert self.nats(credential.jwt)[self.TAGS_KEY] == [kind.value]

    def test_a_simulated_and_a_service_credential_are_separate(self) -> None:
        account = self.account(self.operator())
        issuer = self.issuer()
        simulated = issuer.issue(account, self.OPERATOR_ID, CredentialKind.SIMULATED, self.CREDENTIAL_NAME)
        service = issuer.issue(account, self.OPERATOR_ID, CredentialKind.SERVICE, self.CREDENTIAL_NAME)
        assert simulated.public_key != service.public_key
        assert simulated.seed.get_secret_value() != service.seed.get_secret_value()

    def test_the_system_kind_is_refused_for_an_operator_credential(self) -> None:
        account = self.account(self.operator())
        with pytest.raises(SECredentialIssuerInvalidKindError):
            self.issuer().issue(account, self.OPERATOR_ID, CredentialKind.SYSTEM, self.CREDENTIAL_NAME)

    def test_an_operator_id_that_is_not_the_account_name_is_refused(self) -> None:
        account = self.account(self.operator())
        with pytest.raises(SECredentialIssuerAccountMismatchError):
            self.issuer().issue(account, self.OTHER_OPERATOR_ID, CredentialKind.SERVICE, self.CREDENTIAL_NAME)

    def test_the_system_credential_belongs_to_the_system_account(self) -> None:
        operator = self.operator()
        credential = self.issuer().issue_system(operator, self.CREDENTIAL_NAME)
        assert credential.kind == CredentialKind.SYSTEM
        assert credential.operator_id is None
        claims = self.claims(credential.jwt)
        assert claims[self.ISS_KEY] == operator.system_account.public_key
        assert claims[self.SUB_KEY] == credential.public_key

    def test_the_system_credential_has_no_subject_allow_lists_and_is_tagged_system(self) -> None:
        credential = self.issuer().issue_system(self.operator(), self.CREDENTIAL_NAME)
        nats = self.nats(credential.jwt)
        assert self.PUB_KEY not in nats
        assert self.SUBSCRIBE_KEY not in nats
        assert nats[self.TAGS_KEY] == [self.SYSTEM_TAG]

    def test_the_creds_file_holds_the_jwt_then_the_seed(self) -> None:
        _, credential = self.issue(CredentialKind.SERVICE)
        lines = self.issuer().creds_file(credential).splitlines()
        positions = [
            lines.index(self.JWT_BEGIN),
            lines.index(credential.jwt),
            lines.index(self.JWT_END),
            lines.index(self.SEED_BEGIN),
            lines.index(credential.seed.get_secret_value()),
            lines.index(self.SEED_END),
        ]
        assert positions == sorted(positions)
