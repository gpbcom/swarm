from __future__ import annotations

# Standard library imports
import shutil
from functools import partial
from pathlib import Path
from typing import Iterator, List, Optional, Tuple
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from services.simulator.tests.helpers import OPERATOR_ID
from simulator.models.registry.registered_drone import RegisteredDrone
from swarm_nats.models.enums import CredentialKind
from tests.deploy.nats.helpers import free_port, issuers, operator_mode_config, write_creds
from tests.deploy.nats.nats_server_process import NatsServerProcess

Cell = Tuple[str, int, Path, Path]

CELL_NAME = "cell"
SIMULATED_NAME = "squad-sim"
SERVICE_NAME = "service"
CONFIG_FOLDER = "config"
CREDS_FOLDER = "creds"
JETSTREAM_FOLDER = "jetstream"
APP_NAME = "app.yaml"
SQUAD_NAME = "simulated_squad.yaml"
MAPPING_NAME = "command_mapping.yaml"
FLIGHT_LOG_NAME = "flight_log.sqlite3"
UNUSED_CREDS_NAME = "unused.creds"
UNUSED_SERVER = "nats://127.0.0.1:4222"
ENCODING = "utf-8"
QUEUE_GROUP = "simulator"
SQUAD_HEAD = "drones:\n"
DRONE_ENTRY = (
    "  - drone_id: {drone_id}\n    kind: {kind}\n    host: {host}\n    port: {port}\n    system_id: {system_id}\n"
)
MAPPING_TEXT = "commands:\n  hold:\n    command_id: 193\n    param1: 0.0\n  return_home:\n    command_id: 20\n"
APP_TEMPLATE = """operator_id: {operator_id}
nats:
  servers: ["{server}"]
  credentials_path: {creds}
  connect_timeout_s: 5.0
responder:
  subject: op.{operator_id}.mission.*.command
  queue_group: {queue_group}
  idempotency_bucket: idempotency
  idempotency_ttl_s: 600.0
  replicas: 1
  status_interval_s: 0.2
registry:
  squad_catalog_path: {squad}
  command_mapping_path: {mapping}
flight:
  heartbeat_timeout_s: 2.0
  arm_timeout_s: 2.0
  route_timeout_s: 2.0
  status_interval_s: 0.1
flight_log_path: {flight_log}
"""


def write_app_config(
    directory: Path,
    drones: List[RegisteredDrone],
    server: str = UNUSED_SERVER,
    creds: Optional[Path] = None,
) -> Path:
    """Write the app.yaml of the Simulator and the catalogs of stand-in Drones it points at, to a folder."""
    directory.mkdir(parents=True, exist_ok=True)
    squad = directory / SQUAD_NAME
    mapping = directory / MAPPING_NAME
    entries = "".join(
        DRONE_ENTRY.format(
            drone_id=drone.drone_id,
            kind=drone.kind,
            host=drone.host,
            port=drone.port,
            system_id=drone.system_id,
        )
        for drone in drones
    )
    squad.write_text(SQUAD_HEAD + entries, encoding=ENCODING)
    mapping.write_text(MAPPING_TEXT, encoding=ENCODING)
    if creds is None:
        creds = directory / UNUSED_CREDS_NAME
    path = directory / APP_NAME
    path.write_text(
        APP_TEMPLATE.format(
            operator_id=OPERATOR_ID,
            server=server,
            creds=creds,
            queue_group=QUEUE_GROUP,
            squad=squad,
            mapping=mapping,
            flight_log=directory / FLIGHT_LOG_NAME,
        ),
        encoding=ENCODING,
    )
    return path


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
