from __future__ import annotations

# Standard library imports
from logging import ERROR
from pathlib import Path
from typing import ClassVar, Tuple
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_models.accounts.issued_credential import IssuedCredential
from swarm_models.enums import CredentialKind
from swarm_models.simulation.credentials.exceptions import (
    SESimulatedCredentialsNotSimulatedError,
    SESimulatedCredentialsUnreadableError,
)
from swarm_service.shared.accounts.account_issuer import AccountIssuer
from swarm_service.shared.accounts.credential_issuer import CredentialIssuer
from swarm_service.shared.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_service.shared.accounts.nkey_factory import NkeyFactory
from swarm_service.shared.accounts.operator_issuer import OperatorIssuer
from swarm_service.simulation.credentials.simulated_credentials_guard import SimulatedCredentialsGuard


class TestSimulatedCredentialsGuard:
    OPERATOR_NAME: ClassVar[str] = "cell"
    OPERATOR_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7b")
    CREDENTIAL_NAME: ClassVar[str] = "squad"
    CREDS_NAME: ClassVar[str] = "squad.creds"
    MISSING_NAME: ClassVar[str] = "missing.creds"
    GARBAGE_TEXT: ClassVar[str] = "this is not a credentials file\n"
    ENCODING: ClassVar[str] = "utf-8"

    def issue(self, tmp_path: Path, kind: CredentialKind) -> Tuple[IssuedCredential, Path]:
        credential_issuer = CredentialIssuer(NkeyFactory(), NatsJwtSigner())
        operator = OperatorIssuer(NkeyFactory(), NatsJwtSigner()).issue(self.OPERATOR_NAME)
        account = AccountIssuer(NkeyFactory(), NatsJwtSigner()).issue(operator, self.OPERATOR_ID)
        credential = credential_issuer.issue(account, self.OPERATOR_ID, kind, self.CREDENTIAL_NAME)
        path = tmp_path / self.CREDS_NAME
        path.write_text(credential_issuer.creds_file(credential), encoding=self.ENCODING)
        return credential, path

    def test_a_simulated_credential_passes(self, tmp_path: Path) -> None:
        _, path = self.issue(tmp_path, CredentialKind.SIMULATED)
        SimulatedCredentialsGuard().check(str(path))

    @pytest.mark.parametrize("kind", [CredentialKind.SERVICE, CredentialKind.EDGE])
    def test_a_credential_of_another_kind_is_refused(self, tmp_path: Path, kind: CredentialKind) -> None:
        _, path = self.issue(tmp_path, kind)
        with pytest.raises(SESimulatedCredentialsNotSimulatedError):
            SimulatedCredentialsGuard().check(str(path))

    def test_a_missing_file_is_unreadable(self, tmp_path: Path) -> None:
        with pytest.raises(SESimulatedCredentialsUnreadableError):
            SimulatedCredentialsGuard().check(str(tmp_path / self.MISSING_NAME))

    def test_a_garbage_file_is_unreadable(self, tmp_path: Path) -> None:
        path = tmp_path / self.CREDS_NAME
        path.write_text(self.GARBAGE_TEXT, encoding=self.ENCODING)
        with pytest.raises(SESimulatedCredentialsUnreadableError):
            SimulatedCredentialsGuard().check(str(path))

    def test_a_refusal_logs_an_error_without_the_seed_or_the_jwt(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        credential, path = self.issue(tmp_path, CredentialKind.SERVICE)
        with caplog.at_level(ERROR), pytest.raises(SESimulatedCredentialsNotSimulatedError):
            SimulatedCredentialsGuard().check(str(path))
        assert any(record.levelno == ERROR for record in caplog.records)
        assert credential.seed.get_secret_value() not in caplog.text
        assert credential.jwt not in caplog.text
