from __future__ import annotations

# Standard library imports
import asyncio
import os
import select
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

# Third-party imports
import httpx
import yaml

# First-party imports
from swarm_clients.shared.nats.nats_requester import NatsRequester
from swarm_models.commands.command import Command
from swarm_models.config.app_config import AppConfig
from swarm_models.enums import CredentialKind, FlightLogEntryKind, SimulatedDroneKind
from swarm_models.simulation.commands.command_reply import CommandReply
from swarm_nats.models.bus.exceptions import SENatsNoResponderError, SENatsRequestDeadlineExceededError
from tests.infra.nats.helpers import issuers, write_creds

Endpoint = Tuple[UUID, SimulatedDroneKind, str, int, int]
FlightLogRow = Tuple[str, str, int]

REPO_ROOT = Path(__file__).resolve().parents[3]
APP_DIR = REPO_ROOT / "backend" / "apps" / "simulator"
RUST_DIR = REPO_ROOT / "rust"
BINARY_PATH = RUST_DIR / "target" / "debug" / "swarm-synthetic-drones"
COMMAND_MAPPING_PATH = APP_DIR / AppConfig.CONF_FOLDER / "catalogs" / "command_mapping.yaml"
LOGGER_PATH = APP_DIR / AppConfig.CONF_FOLDER / AppConfig.LOGGER_FILE
SCRIPT_NAME = "swarm-simulator-serve"
SIMULATIONS_URL = "http://{host}:{port}/v1/simulations"
OPENAPI_URL = "http://{host}:{port}/v1/openapi.json"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
FLY_KEY_PREFIX = "simulation-"
HOST = "127.0.0.1"
ENCODING = "utf-8"
READY_LINE = "ready"
READY_TIMEOUT_S = 30.0
BIND_ATTEMPTS = 10
SYNTHETIC_COUNT = 10
SYNTHETIC_SPEED_M_S = 50
SYNTHETIC_TICK_MS = 20
FLY_TIMEOUT_S = 180.0
SERVE_START_TIMEOUT_S = 30.0
STOP_TIMEOUT_S = 30.0
HTTP_TIMEOUT_S = 5.0
POLL_INTERVAL_S = 0.1
SQUAD_STATUS_INTERVAL_S = 1.0
UUID_TEMPLATE = "0190a5b2-7c3e-7d4f-8a1b-{index:012x}"
PX4_DRONE_INDEX = 100
PX4_SYSTEM_ID = 1
PX4_CONTAINER_PORT = 18570
OPERATOR_ID = UUID(UUID_TEMPLATE.format(index=0xA0))
MISSION_ID = UUID(UUID_TEMPLATE.format(index=0xB0))
ISSUER_ID = UUID(UUID_TEMPLATE.format(index=0xC0))
COMMAND_ID = UUID(UUID_TEMPLATE.format(index=0xD0))
UNKNOWN_DRONE_ID = UUID(UUID_TEMPLATE.format(index=0xE0))
QUEUE_GROUP = "simulator"
WARNING_WORD = "WARNING"

DRONES_KEY = "drones"
DRONE_ID_KEY = "drone_id"
KIND_KEY = "kind"
HOST_KEY = "host"
PORT_KEY = "port"
SYSTEM_ID_KEY = "system_id"
OPERATOR_ID_KEY = "operator_id"
NATS_KEY = "nats"
SERVERS_KEY = "servers"
CREDENTIALS_PATH_KEY = "credentials_path"
RESPONDER_KEY = "responder"
SUBJECT_KEY = "subject"
QUEUE_GROUP_KEY = "queue_group"
REPLICAS_KEY = "replicas"
REGISTRY_KEY = "registry"
SQUAD_CATALOG_PATH_KEY = "squad_catalog_path"
COMMAND_MAPPING_PATH_KEY = "command_mapping_path"
SIMULATED_HOSTS_KEY = "simulated_hosts"
ROUTE_KEY = "route"
SIDE_M_KEY = "side_m"
ALTITUDE_M_KEY = "altitude_m"
FLIGHT_KEY = "flight"
HEARTBEAT_TIMEOUT_KEY = "heartbeat_timeout_s"
ARM_TIMEOUT_KEY = "arm_timeout_s"
ROUTE_TIMEOUT_KEY = "route_timeout_s"
STATUS_INTERVAL_KEY = "status_interval_s"
FLIGHT_LOG_PATH_KEY = "flight_log_path"
REST_KEY = "rest"
REST_HOST_KEY = "host"
REST_PORT_KEY = "port"
MISSION_ID_KEY = "mission_id"
SIMULATED_NAME = "squad-sim"
OPERATOR_NAME = "cell"
SQUAD_CATALOG_NAME = "simulated_squad.yaml"
APP_CONFIG_NAME = "app.yaml"
FLIGHT_LOG_NAME = "flight_log.sqlite3"
NATS_URL_DEFAULT = "nats://127.0.0.1:4222"
CREDS_FOLDER = "creds"
ROUTE_SIDE_M = 20
ROUTE_ALTITUDE_M = 10
HEARTBEAT_TIMEOUT_S = 20
ARM_TIMEOUT_S = 30
ROUTE_TIMEOUT_S = 90
SIMULATED_COLUMN = "simulated"
ROWS_QUERY = "SELECT drone_id, kind, simulated FROM flight_log_entries ORDER BY rowid"
TABLE_INFO_QUERY = "PRAGMA table_info(flight_log_entries)"
NAME_INDEX = 1
PRIMARY_KEY_INDEX = 5
UNSIMULATED_VALUE = "0"
COPY_QUERY = "INSERT INTO flight_log_entries ({columns}) SELECT {values} FROM flight_log_entries LIMIT 1"
COMMAND_SUBJECT = "op.{operator}.mission.{mission}.command"
COMMAND_WILDCARD_SUBJECT = "op.{operator}.mission.*.command"
KEY_PREFIX = "command-"
REQUEST_DEADLINE_S = 2.0
SERVE_READY_TIMEOUT_S = 30.0
STDERR_NAME = "serve.stderr"
DOCKER_IMAGE_ENV = "SWARM_PX4_SITL_IMAGE"
DOCKER_IMAGE_DEFAULT = "swarm-px4-sitl:local"


def squad_drone_id(index: int) -> UUID:
    """Return the fixed version 7 identifier of the Drone at this index."""
    return UUID(UUID_TEMPLATE.format(index=index))


def free_udp_base_port(count: int) -> int:
    """Find a base port whose ``count`` consecutive UDP ports are all free."""
    for _ in range(BIND_ATTEMPTS):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.bind((HOST, 0))
            base = int(probe.getsockname()[1])
        sockets: List[socket.socket] = []
        try:
            for offset in range(count):
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sockets.append(sock)
                sock.bind((HOST, base + offset))
        except OSError:
            continue
        finally:
            for sock in sockets:
                sock.close()
        return base
    raise AssertionError(f"No free run of {count} UDP ports was found.")


def free_udp_port() -> int:
    """Return a free UDP port."""
    return free_udp_base_port(1)


def start_synthetic_drones(binary: Path, base_port: int) -> Optional[subprocess.Popen[str]]:
    """Start the binary on this base port and wait for its ready line, or return ``None`` when it did not start."""
    process = subprocess.Popen(
        [
            str(binary),
            "--count",
            str(SYNTHETIC_COUNT),
            "--bind",
            HOST,
            "--base-port",
            str(base_port),
            "--speed-m-s",
            str(SYNTHETIC_SPEED_M_S),
            "--tick-ms",
            str(SYNTHETIC_TICK_MS),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding=ENCODING,
    )
    assert process.stdout is not None
    deadline = time.monotonic() + READY_TIMEOUT_S
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return None
        readable, _, _ = select.select([process.stdout], [], [], POLL_INTERVAL_S)
        if readable and process.stdout.readline().strip() == READY_LINE:
            return process
    stop_process(process)
    return None


def stop_process(process: subprocess.Popen[str]) -> None:
    """Kill a child process and wait for it."""
    process.kill()
    process.wait()
    if process.stdout is not None:
        process.stdout.close()


def synthetic_endpoints(base_port: int) -> List[Endpoint]:
    """Return the registry entries of the ten synthetic Drones started on this base port."""
    endpoints: List[Endpoint] = []
    for index in range(SYNTHETIC_COUNT):
        endpoints.append((squad_drone_id(index + 1), SimulatedDroneKind.SYNTHETIC, HOST, base_port + index, index + 1))
    return endpoints


def px4_endpoint(port: int) -> Endpoint:
    """Return the registry entry of a PX4 SITL Drone listening on this port."""
    return (squad_drone_id(PX4_DRONE_INDEX), SimulatedDroneKind.PX4_SITL, HOST, port, PX4_SYSTEM_ID)


def script_path() -> Path:
    """Return the path of the ``swarm-simulator-serve`` console script of this environment."""
    return Path(sys.executable).parent / SCRIPT_NAME


def write_squad_catalog(tmp_path: Path, endpoints: List[Endpoint]) -> Path:
    """Write the catalog of the simulated Squad, one entry per endpoint."""
    drones = []
    for drone_id, kind, host, port, system_id in endpoints:
        drones.append(
            {
                DRONE_ID_KEY: str(drone_id),
                KIND_KEY: kind.value,
                HOST_KEY: host,
                PORT_KEY: port,
                SYSTEM_ID_KEY: system_id,
            }
        )
    path = tmp_path / SQUAD_CATALOG_NAME
    path.write_text(yaml.safe_dump({DRONES_KEY: drones}, sort_keys=False), encoding=ENCODING)
    return path


def flight_log_path(tmp_path: Path) -> Path:
    """Return where the Flight log of a run in ``tmp_path`` is written."""
    return tmp_path / FLIGHT_LOG_NAME


def write_app_config(
    tmp_path: Path,
    catalog_path: Path,
    credentials_path: Optional[Path] = None,
    nats_url: str = NATS_URL_DEFAULT,
    heartbeat_timeout_s: float = HEARTBEAT_TIMEOUT_S,
    arm_timeout_s: float = ARM_TIMEOUT_S,
    route_timeout_s: float = ROUTE_TIMEOUT_S,
) -> Path:
    """Write the folder of the simulator app for one run, with the Flight log in ``tmp_path``, and return it.

    The folder holds ``conf/app.yaml`` and ``conf/logger.yaml``, as the image's ``/app`` does. Without a credentials
    file, simulated credentials are written.
    """
    if credentials_path is None:
        credentials_path = write_simulated_creds(tmp_path)
    config = {
        REST_KEY: {REST_HOST_KEY: HOST, REST_PORT_KEY: free_tcp_port()},
        OPERATOR_ID_KEY: str(OPERATOR_ID),
        NATS_KEY: {SERVERS_KEY: [nats_url], CREDENTIALS_PATH_KEY: str(credentials_path)},
        RESPONDER_KEY: {
            SUBJECT_KEY: COMMAND_WILDCARD_SUBJECT.format(operator=OPERATOR_ID),
            QUEUE_GROUP_KEY: QUEUE_GROUP,
            REPLICAS_KEY: 1,
        },
        REGISTRY_KEY: {
            SQUAD_CATALOG_PATH_KEY: str(catalog_path),
            COMMAND_MAPPING_PATH_KEY: str(COMMAND_MAPPING_PATH),
            SIMULATED_HOSTS_KEY: [HOST],
        },
        ROUTE_KEY: {SIDE_M_KEY: ROUTE_SIDE_M, ALTITUDE_M_KEY: ROUTE_ALTITUDE_M},
        FLIGHT_KEY: {
            HEARTBEAT_TIMEOUT_KEY: heartbeat_timeout_s,
            ARM_TIMEOUT_KEY: arm_timeout_s,
            ROUTE_TIMEOUT_KEY: route_timeout_s,
            STATUS_INTERVAL_KEY: SQUAD_STATUS_INTERVAL_S,
        },
        FLIGHT_LOG_PATH_KEY: str(flight_log_path(tmp_path)),
    }
    conf = tmp_path / AppConfig.CONF_FOLDER
    conf.mkdir(parents=True, exist_ok=True)
    (conf / AppConfig.APP_FILE).write_text(yaml.safe_dump(config, sort_keys=False), encoding=ENCODING)
    shutil.copy(LOGGER_PATH, conf / AppConfig.LOGGER_FILE)
    return tmp_path


def free_tcp_port() -> int:
    """Return a free TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((HOST, 0))
        return int(probe.getsockname()[1])


def write_simulated_creds(tmp_path: Path) -> Path:
    """Write credentials of kind simulated for the Operator of the run, signed by a throwaway operator."""
    operator_issuer, account_issuer, credential_issuer = issuers()
    account = account_issuer.issue(operator_issuer.issue(OPERATOR_NAME), OPERATOR_ID)
    simulated = credential_issuer.issue(account, OPERATOR_ID, CredentialKind.SIMULATED, SIMULATED_NAME)
    return write_creds(tmp_path / CREDS_FOLDER, simulated, credential_issuer)


def rest_port(app_folder: Path) -> int:
    """Read the port the app of a run serves on."""
    config = yaml.safe_load((app_folder / AppConfig.CONF_FOLDER / AppConfig.APP_FILE).read_text(encoding=ENCODING))
    return int(config[REST_KEY][REST_PORT_KEY])


def start_serve(app_folder: Path, stderr_path: Path) -> subprocess.Popen[bytes]:
    """Start the simulator app from its folder, with its standard error written to a file."""
    environment = dict(os.environ)
    environment[AppConfig.APP_ROOT_KEY] = str(app_folder)
    stderr = stderr_path.open("wb")
    return subprocess.Popen(
        [str(script_path())], cwd=app_folder, env=environment, stdout=subprocess.DEVNULL, stderr=stderr
    )


def stop_serve(process: subprocess.Popen[bytes]) -> None:
    """Stop the app and wait for it."""
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=STOP_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def wait_until_serving(port: int, process: subprocess.Popen[bytes]) -> None:
    """Wait until the app answers its OpenAPI document."""
    deadline = time.monotonic() + SERVE_START_TIMEOUT_S
    while time.monotonic() < deadline:
        assert process.poll() is None, f"The simulator app stopped with code {process.returncode}."
        try:
            if httpx.get(OPENAPI_URL.format(host=HOST, port=port), timeout=HTTP_TIMEOUT_S).is_success:
                return
        except httpx.TransportError:
            time.sleep(POLL_INTERVAL_S)
    raise AssertionError("The simulator app did not serve in time.")


def ended_flights(path: Path) -> int:
    """Count the Drones whose flight has ended in the Flight log, completed or failed."""
    if not path.is_file():
        return 0
    try:
        rows = flight_log_rows(path)
    except sqlite3.OperationalError:
        return 0
    return count_kind(rows, FlightLogEntryKind.ROUTE_COMPLETED) + count_kind(rows, FlightLogEntryKind.ROUTE_FAILED)


def run_fly(app_folder: Path, mission_id: UUID, drones: int, timeout_s: float = FLY_TIMEOUT_S) -> httpx.Response:
    """Serve the app, start the flight of the Squad with ``POST /v1/simulations``, and wait until every Drone ends."""
    port = rest_port(app_folder)
    process = start_serve(app_folder, app_folder / STDERR_NAME)
    try:
        wait_until_serving(port, process)
        response = httpx.post(
            SIMULATIONS_URL.format(host=HOST, port=port),
            json={MISSION_ID_KEY: str(mission_id)},
            headers={IDEMPOTENCY_KEY_HEADER: FLY_KEY_PREFIX + str(mission_id)},
            timeout=HTTP_TIMEOUT_S,
        )
        deadline = time.monotonic() + timeout_s
        while response.is_success and ended_flights(flight_log_path(app_folder)) < drones:
            assert time.monotonic() < deadline, "The simulated flight did not end in time."
            assert process.poll() is None, "The simulator app stopped during the flight."
            time.sleep(POLL_INTERVAL_S)
        return response
    finally:
        stop_serve(process)


def flight_log_rows(path: Path) -> List[FlightLogRow]:
    """Read every Flight log row as ``(drone_id, kind, simulated)``, in insertion order."""
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(ROWS_QUERY).fetchall()
    return [(str(row[0]), str(row[1]), int(row[2])) for row in rows]


def kinds_of(rows: List[FlightLogRow], drone_id: UUID) -> List[str]:
    """Return the kinds logged for one Drone, in order."""
    return [kind for logged, kind, _ in rows if logged == str(drone_id)]


def count_kind(rows: List[FlightLogRow], kind: FlightLogEntryKind) -> int:
    """Count the rows of one kind."""
    return len([row for row in rows if row[1] == kind.value])


def insert_unsimulated_copy(path: Path) -> None:
    """Insert a copy of the first Flight log row with ``simulated`` set to 0."""
    with closing(sqlite3.connect(path)) as connection:
        table = connection.execute(TABLE_INFO_QUERY).fetchall()
        columns = [str(row[NAME_INDEX]) for row in table if not row[PRIMARY_KEY_INDEX]]
        values = [UNSIMULATED_VALUE if column == SIMULATED_COLUMN else column for column in columns]
        connection.execute(COPY_QUERY.format(columns=", ".join(columns), values=", ".join(values)))
        connection.commit()


async def request_until_answered(
    requester: NatsRequester, command: Command, process: subprocess.Popen[bytes]
) -> CommandReply:
    """Send the command until the serving Simulator answers it, always with the same idempotency key."""
    subject = COMMAND_SUBJECT.format(operator=OPERATOR_ID, mission=command.mission_id)
    deadline = time.monotonic() + SERVE_READY_TIMEOUT_S
    while time.monotonic() < deadline:
        assert process.poll() is None, "The simulator app exited before it answered."
        try:
            return await requester.request(
                subject, command, CommandReply, KEY_PREFIX + str(command.id), REQUEST_DEADLINE_S
            )
        except (SENatsNoResponderError, SENatsRequestDeadlineExceededError):
            await asyncio.sleep(POLL_INTERVAL_S)
    raise AssertionError("The simulator app never answered the command.")


def docker_image() -> str:
    """Return the name of the PX4 SITL image."""
    return os.environ.get(DOCKER_IMAGE_ENV, DOCKER_IMAGE_DEFAULT)
