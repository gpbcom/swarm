from __future__ import annotations

# Standard library imports
import shutil
from pathlib import Path
from typing import Iterator, List, Tuple

# Third-party imports
import nats
import pytest
from nats.errors import TimeoutError as NatsTimeoutError

# First-party imports
from swarm_nats.models.enums import CredentialKind
from swarm_nats.models.subjects.operator_subjects import OperatorSubjects
from tests.infra.nats.helpers import (
    OPERATOR_A_ID,
    OPERATOR_B_ID,
    free_port,
    issuers,
    operator_mode_config,
    violation_seen,
    write_creds,
)
from tests.infra.nats.nats_server_process import NatsServerProcess


@pytest.mark.skipif(shutil.which("nats-server") is None, reason="nats-server is not installed")
class TestOperatorIsolation:
    OPERATOR_NAME = "cell"
    SERVICE_A = "service-a"
    SERVICE_B = "service-b"
    EVENT = "position"
    PAYLOAD = b"x"
    VIOLATION_WAIT_S = 2.0
    SILENCE_WAIT_S = 1.0
    DELIVERY_WAIT_S = 2.0

    @pytest.fixture
    def cell(self, tmp_path: Path) -> Iterator[Tuple[str, Path, Path]]:
        operator_issuer, account_issuer, credential_issuer = issuers()
        operator = operator_issuer.issue(self.OPERATOR_NAME)
        account_a = account_issuer.issue(operator, OPERATOR_A_ID)
        account_b = account_issuer.issue(operator, OPERATOR_B_ID)
        credential_a = credential_issuer.issue(account_a, OPERATOR_A_ID, CredentialKind.SERVICE, self.SERVICE_A)
        credential_b = credential_issuer.issue(account_b, OPERATOR_B_ID, CredentialKind.SERVICE, self.SERVICE_B)
        creds_a = write_creds(tmp_path / "creds", credential_a, credential_issuer)
        creds_b = write_creds(tmp_path / "creds", credential_b, credential_issuer)
        port = free_port()
        config = operator_mode_config(port, free_port(), operator, [account_a, account_b])
        server = NatsServerProcess(tmp_path, config, port)
        server.spawn()
        yield server.url, creds_a, creds_b
        server.kill()

    async def on_error(self, error: Exception) -> None:
        self.errors.append(error)

    async def test_a_publication_on_another_operators_subject_is_refused(self, cell: Tuple[str, Path, Path]) -> None:
        url, creds_a, _ = cell
        self.errors: List[Exception] = []
        client = await nats.connect(url, user_credentials=str(creds_a), error_cb=self.on_error)
        await client.publish(OperatorSubjects(operator_id=OPERATOR_B_ID).fleet(self.EVENT), self.PAYLOAD)
        seen = await violation_seen(self.errors, self.VIOLATION_WAIT_S)
        await client.close()
        assert seen

    async def test_another_operators_subscriber_receives_nothing(self, cell: Tuple[str, Path, Path]) -> None:
        url, creds_a, creds_b = cell
        self.errors = []
        publisher = await nats.connect(url, user_credentials=str(creds_a), error_cb=self.on_error)
        subscriber = await nats.connect(url, user_credentials=str(creds_b), error_cb=self.on_error)
        subscription = await subscriber.subscribe(OperatorSubjects(operator_id=OPERATOR_B_ID).all())
        await subscriber.flush()
        await publisher.publish(OperatorSubjects(operator_id=OPERATOR_B_ID).fleet(self.EVENT), self.PAYLOAD)
        await publisher.flush()
        with pytest.raises(NatsTimeoutError):
            await subscription.next_msg(timeout=self.SILENCE_WAIT_S)
        await publisher.close()
        await subscriber.close()

    async def test_a_subscription_to_another_operators_subjects_is_refused(self, cell: Tuple[str, Path, Path]) -> None:
        url, creds_a, _ = cell
        self.errors = []
        client = await nats.connect(url, user_credentials=str(creds_a), error_cb=self.on_error)
        await client.subscribe(OperatorSubjects(operator_id=OPERATOR_B_ID).all())
        seen = await violation_seen(self.errors, self.VIOLATION_WAIT_S)
        await client.close()
        assert seen

    async def test_a_publication_on_its_own_subject_reaches_its_subscriber(self, cell: Tuple[str, Path, Path]) -> None:
        url, creds_a, _ = cell
        self.errors = []
        client = await nats.connect(url, user_credentials=str(creds_a), error_cb=self.on_error)
        subscription = await client.subscribe(OperatorSubjects(operator_id=OPERATOR_A_ID).all())
        await client.flush()
        await client.publish(OperatorSubjects(operator_id=OPERATOR_A_ID).fleet(self.EVENT), self.PAYLOAD)
        message = await subscription.next_msg(timeout=self.DELIVERY_WAIT_S)
        await client.close()
        assert message.data == self.PAYLOAD
        assert self.errors == []
