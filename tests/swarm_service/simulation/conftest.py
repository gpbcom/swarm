from __future__ import annotations

# Standard library imports
import shutil
from functools import partial
from pathlib import Path
from typing import Iterator, Tuple
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import CredentialKind
from tests.fakes.mavlink.helpers import OPERATOR_ID, write_app_config
from tests.infra.nats.helpers import free_port, issuers, operator_mode_config, write_creds
from tests.infra.nats.nats_server_process import NatsServerProcess

Cell = Tuple[str, int, Path, Path]

CELL_NAME = "cell"
SIMULATED_NAME = "squad-sim"
SERVICE_NAME = "service"
CONFIG_FOLDER = "config"
CREDS_FOLDER = "creds"
JETSTREAM_FOLDER = "jetstream"


@pytest.fixture
def nats_cell(tmp_path: Path) -> Iterator[Cell]:
    """A NATS server in operator mode with JetStream and one account, with simulated and service credentials."""
    if shutil.which(NatsServerProcess.BINARY) is None:
        pytest.skip("nats-server is not installed")
    operator_issuer, account_issuer, credential_issuer = issuers()
    operator_id = UUID(str(OPERATOR_ID))
    operator = operator_issuer.issue(CELL_NAME)
    account = account_issuer.issue(operator, operator_id)
    simulated = credential_issuer.issue(account, operator_id, CredentialKind.SIMULATED, SIMULATED_NAME)
    service = credential_issuer.issue(account, operator_id, CredentialKind.SERVICE, SERVICE_NAME)
    simulated_creds = write_creds(tmp_path / CREDS_FOLDER, simulated, credential_issuer)
    service_creds = write_creds(tmp_path / CREDS_FOLDER, service, credential_issuer)
    port = free_port()
    monitor_port = free_port()
    config = operator_mode_config(
        port, monitor_port, operator, [account], store_dir=tmp_path / JETSTREAM_FOLDER, server_name=CELL_NAME
    )
    server = NatsServerProcess(tmp_path, config, port)
    server.spawn()
    yield server.url, monitor_port, simulated_creds, service_creds
    server.kill()


@pytest.fixture
def app_config(tmp_path: Path) -> partial[Path]:
    """Give a function that writes the Simulator configuration and its catalogs in a folder of the test."""
    return partial(write_app_config, tmp_path / CONFIG_FOLDER)
