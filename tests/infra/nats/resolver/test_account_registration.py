from __future__ import annotations

# Standard library imports
import shutil
from pathlib import Path
from typing import Iterator, Tuple

# Third-party imports
import pytest

# First-party imports
from swarm_nats.models.accounts.issued_account import IssuedAccount
from swarm_nats.models.enums import CredentialKind
from tests.deploy.nats.helpers import (
    OPERATOR_A_ID,
    connects,
    free_port,
    full_resolver_config,
    issuers,
    push_account,
    write_creds,
)
from tests.deploy.nats.nats_server_process import NatsServerProcess

Cell = Tuple[str, IssuedAccount, IssuedAccount, Path, Path, Path]


@pytest.mark.skipif(shutil.which("nats-server") is None, reason="nats-server is not installed")
class TestAccountRegistration:
    OPERATOR_NAME = "cell"
    OTHER_OPERATOR_NAME = "other"
    SERVICE_NAME = "service"
    SYSTEM_NAME = "system"
    PUSH_TIMEOUT_S = 5.0

    @pytest.fixture
    def cell(self, tmp_path: Path) -> Iterator[Cell]:
        operator_issuer, account_issuer, credential_issuer = issuers()
        operator = operator_issuer.issue(self.OPERATOR_NAME)
        other = operator_issuer.issue(self.OTHER_OPERATOR_NAME)
        account = account_issuer.issue(operator, OPERATOR_A_ID)
        foreign = account_issuer.issue(other, OPERATOR_A_ID)
        service = credential_issuer.issue(account, OPERATOR_A_ID, CredentialKind.SERVICE, self.SERVICE_NAME)
        system = credential_issuer.issue_system(operator, self.SYSTEM_NAME)
        foreign_service = credential_issuer.issue(foreign, OPERATOR_A_ID, CredentialKind.SERVICE, self.SERVICE_NAME)
        service_creds = write_creds(tmp_path / "creds", service, credential_issuer)
        foreign_creds = write_creds(tmp_path / "foreign", foreign_service, credential_issuer)
        system_creds = write_creds(tmp_path / "creds", system, credential_issuer)
        port = free_port()
        config = full_resolver_config(port, free_port(), operator, tmp_path / "resolver")
        server = NatsServerProcess(tmp_path, config, port)
        server.spawn()
        yield server.url, account, foreign, service_creds, system_creds, foreign_creds
        server.kill()

    async def test_an_account_that_was_not_pushed_refuses_its_credentials(self, cell: Cell) -> None:
        url, _, _, service_creds, _, _ = cell
        assert not await connects(url, service_creds)

    async def test_a_pushed_account_accepts_its_credentials(self, cell: Cell) -> None:
        url, account, _, service_creds, system_creds, _ = cell
        await push_account(url, system_creds, account, self.PUSH_TIMEOUT_S)
        assert await connects(url, service_creds)

    async def test_an_account_signed_by_another_operator_never_accepts_its_credentials(self, cell: Cell) -> None:
        url, _, foreign, _, system_creds, foreign_creds = cell
        await push_account(url, system_creds, foreign, self.PUSH_TIMEOUT_S)
        assert not await connects(url, foreign_creds)
