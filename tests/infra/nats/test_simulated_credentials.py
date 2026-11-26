from __future__ import annotations

# Standard library imports
import shutil
from pathlib import Path
from typing import ClassVar, Iterator, List, Tuple

# Third-party imports
import nats
import pytest

# First-party imports
from swarm_nats.models.accounts.issued_credential import IssuedCredential
from swarm_nats.models.enums import CredentialKind
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from tests.infra.nats.helpers import (
    OPERATOR_A_ID,
    OPERATOR_B_ID,
    connz_users,
    free_port,
    issuers,
    operator_mode_config,
    violation_seen,
    write_creds,
)
from tests.infra.nats.nats_server_process import NatsServerProcess

Cell = Tuple[str, int, IssuedCredential, IssuedCredential, Path, Path]


@pytest.mark.skipif(shutil.which("nats-server") is None, reason="nats-server is not installed")
class TestSimulatedCredentials:
    OPERATOR_NAME = "cell"
    SIMULATED_NAME = "squad-sim"
    SERVICE_NAME = "service"
    NATS_KEY = "nats"
    TAGS_KEY = "tags"
    SIMULATED_TAGS: ClassVar[List[str]] = ["simulated"]
    SERVICE_TAGS: ClassVar[List[str]] = ["service"]
    EVENT = "position"
    PAYLOAD = b"x"
    VIOLATION_WAIT_S = 2.0

    @pytest.fixture
    def cell(self, tmp_path: Path) -> Iterator[Cell]:
        operator_issuer, account_issuer, credential_issuer = issuers()
        operator = operator_issuer.issue(self.OPERATOR_NAME)
        account_a = account_issuer.issue(operator, OPERATOR_A_ID)
        account_b = account_issuer.issue(operator, OPERATOR_B_ID)
        simulated = credential_issuer.issue(account_a, OPERATOR_A_ID, CredentialKind.SIMULATED, self.SIMULATED_NAME)
        service = credential_issuer.issue(account_a, OPERATOR_A_ID, CredentialKind.SERVICE, self.SERVICE_NAME)
        simulated_creds = write_creds(tmp_path / "creds", simulated, credential_issuer)
        service_creds = write_creds(tmp_path / "creds", service, credential_issuer)
        port = free_port()
        monitor_port = free_port()
        config = operator_mode_config(port, monitor_port, operator, [account_a, account_b])
        server = NatsServerProcess(tmp_path, config, port)
        server.spawn()
        yield server.url, monitor_port, simulated, service, simulated_creds, service_creds
        server.kill()

    async def on_error(self, error: Exception) -> None:
        self.errors.append(error)

    def test_the_two_credentials_are_distinct_and_tagged(self, cell: Cell) -> None:
        _, _, simulated, service, _, _ = cell
        signer = NatsJwtSigner()
        assert simulated.public_key != service.public_key
        assert simulated.seed != service.seed
        assert simulated.jwt != service.jwt
        assert signer.decode(simulated.jwt)[self.NATS_KEY][self.TAGS_KEY] == self.SIMULATED_TAGS
        assert signer.decode(service.jwt)[self.NATS_KEY][self.TAGS_KEY] == self.SERVICE_TAGS

    async def test_both_credentials_connect_as_their_own_users(self, cell: Cell) -> None:
        url, monitor_port, simulated, service, simulated_creds, service_creds = cell
        first = await nats.connect(url, user_credentials=str(simulated_creds))
        second = await nats.connect(url, user_credentials=str(service_creds))
        users = connz_users(monitor_port)
        await first.close()
        await second.close()
        assert sorted(users) == sorted([simulated.public_key, service.public_key])

    async def test_the_simulated_credential_is_limited_to_its_operator(self, cell: Cell) -> None:
        url, _, _, _, simulated_creds, _ = cell
        self.errors: List[Exception] = []
        client = await nats.connect(url, user_credentials=str(simulated_creds), error_cb=self.on_error)
        await client.publish(OperatorSubjects(operator_id=OPERATOR_B_ID).fleet(self.EVENT), self.PAYLOAD)
        seen = await violation_seen(self.errors, self.VIOLATION_WAIT_S)
        await client.close()
        assert seen
