from __future__ import annotations

# Standard library imports
import shutil
from pathlib import Path
from typing import Iterator, Tuple

# Third-party imports
import pytest

# First-party imports
from swarm_nats.models.enums import CredentialKind
from tests.deploy.nats.helpers import (
    OPERATOR_A_ID,
    becomes_refused,
    connects,
    free_port,
    full_resolver_config,
    issuers,
    push_account,
    write_creds,
)
from tests.deploy.nats.nats_server_process import NatsServerProcess

Cell = Tuple[str, Path, Path]


@pytest.mark.skipif(shutil.which("nats-server") is None, reason="nats-server is not installed")
class TestEdgeCredentialRevocation:
    OPERATOR_NAME = "cell"
    FIRST_EDGE = "edge-1"
    SECOND_EDGE = "edge-2"
    SYSTEM_NAME = "system"
    PUSH_TIMEOUT_S = 5.0
    REFUSAL_WAIT_S = 5.0

    @pytest.fixture
    def cell(self, tmp_path: Path) -> Iterator[Cell]:
        operator_issuer, account_issuer, credential_issuer = issuers()
        operator = operator_issuer.issue(self.OPERATOR_NAME)
        account = account_issuer.issue(operator, OPERATOR_A_ID)
        first = credential_issuer.issue(account, OPERATOR_A_ID, CredentialKind.EDGE, self.FIRST_EDGE)
        second = credential_issuer.issue(account, OPERATOR_A_ID, CredentialKind.EDGE, self.SECOND_EDGE)
        system = credential_issuer.issue_system(operator, self.SYSTEM_NAME)
        first_creds = write_creds(tmp_path / "creds", first, credential_issuer)
        second_creds = write_creds(tmp_path / "creds", second, credential_issuer)
        system_creds = write_creds(tmp_path / "creds", system, credential_issuer)
        revoked = account_issuer.revoke(operator, account, [first.public_key])
        port = free_port()
        config = full_resolver_config(port, free_port(), operator, tmp_path / "resolver")
        server = NatsServerProcess(tmp_path, config, port)
        server.spawn()
        self.pushes = (server.url, system_creds, account, revoked)
        yield server.url, first_creds, second_creds
        server.kill()

    async def revoke(self) -> None:
        url, system_creds, account, revoked = self.pushes
        await push_account(url, system_creds, account, self.PUSH_TIMEOUT_S)
        await push_account(url, system_creds, revoked, self.PUSH_TIMEOUT_S)

    async def test_a_revoked_edge_credential_is_refused(self, cell: Cell) -> None:
        url, first_creds, _ = cell
        await self.revoke()
        assert await becomes_refused(url, first_creds, self.REFUSAL_WAIT_S)

    async def test_the_other_edge_credential_still_connects(self, cell: Cell) -> None:
        url, _, second_creds = cell
        await self.revoke()
        assert await connects(url, second_creds)
