from __future__ import annotations

import os
import shutil
import socket
import subprocess
import uuid
from pathlib import Path
from typing import Iterator, List, Optional

import pytest

POSTGRES_APP_ROLE = "swarm_app"
POSTGRES_ADMIN_ROLE = "postgres"
LOCALHOST = "127.0.0.1"
POSTGRES_BIN_DIR_VARIABLE = "SWARM_POSTGRES_BIN_DIR"
POSTGRES_SYSTEM_BIN_GLOB = "postgresql/*/bin"
POSTGRES_SYSTEM_ROOT = Path("/usr/lib")
PG_CTL = "pg_ctl"
INITDB = "initdb"
PSQL = "psql"
DSN_TEMPLATE = "postgresql://{role}@{host}:{port}/{database}"
DATABASE_PREFIX = "swarm_test_"
START_TIMEOUT_S = 60
STOP_TIMEOUT_S = 60
COMMAND_TIMEOUT_S = 60
LOG_TAIL_CHARACTERS = 4000
SKIP_REASON = "PostgreSQL binaries are not installed"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((LOCALHOST, 0))
        port: int = probe.getsockname()[1]
    return port


def version_key(path: Path) -> List[int]:
    version = path.parent.parent.name
    return [int(part) for part in version.split(".") if part.isdigit()]


def find_postgres_bin_dir() -> Path:
    found = shutil.which(PG_CTL)
    if found is not None:
        return Path(found).parent
    configured = os.environ.get(POSTGRES_BIN_DIR_VARIABLE)
    if configured and (Path(configured) / PG_CTL).exists():
        return Path(configured)
    candidates = sorted(POSTGRES_SYSTEM_ROOT.glob(f"{POSTGRES_SYSTEM_BIN_GLOB}/{PG_CTL}"), key=version_key)
    if candidates:
        return candidates[-1].parent
    pytest.skip(SKIP_REASON)


def run_psql(bin_dir: Path, port: int, database: str, sql: str, role: str = POSTGRES_ADMIN_ROLE) -> str:
    completed = subprocess.run(
        [
            str(bin_dir / PSQL),
            "-X",
            "-q",
            "-At",
            "-v",
            "ON_ERROR_STOP=1",
            "-h",
            LOCALHOST,
            "-p",
            str(port),
            "-U",
            role,
            "-d",
            database,
            "-c",
            sql,
        ],
        capture_output=True,
        text=True,
        timeout=COMMAND_TIMEOUT_S,
        check=True,
    )
    return completed.stdout


@pytest.fixture(scope="session")
def postgres_bin_dir() -> Path:
    return find_postgres_bin_dir()


@pytest.fixture(scope="session")
def postgres_server(postgres_bin_dir: Path, tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    root = tmp_path_factory.mktemp("postgres")
    data = root / "data"
    sockets = root / "sockets"
    sockets.mkdir()
    log = root / "server.log"
    port = free_port()
    subprocess.run(
        [
            str(postgres_bin_dir / INITDB),
            "-D",
            str(data),
            "-U",
            POSTGRES_ADMIN_ROLE,
            "--auth=trust",
            "--encoding=UTF8",
            "--no-sync",
        ],
        capture_output=True,
        text=True,
        timeout=COMMAND_TIMEOUT_S,
        check=True,
    )
    options = f"-p {port} -c listen_addresses={LOCALHOST} -c unix_socket_directories={sockets} -c fsync=off"
    started = subprocess.run(
        [
            str(postgres_bin_dir / PG_CTL),
            "-D",
            str(data),
            "-l",
            str(log),
            "-w",
            "-t",
            str(START_TIMEOUT_S),
            "-o",
            options,
            "start",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=START_TIMEOUT_S + COMMAND_TIMEOUT_S,
    )
    if started.returncode != 0:
        tail: Optional[str] = log.read_text()[-LOG_TAIL_CHARACTERS:] if log.exists() else started.stderr
        pytest.fail(f"PostgreSQL did not start. Log end:\n{tail}")
    run_psql(
        postgres_bin_dir,
        port,
        POSTGRES_ADMIN_ROLE,
        f"CREATE ROLE {POSTGRES_APP_ROLE} LOGIN NOSUPERUSER NOBYPASSRLS NOCREATEROLE",
    )
    yield DSN_TEMPLATE.format(role=POSTGRES_ADMIN_ROLE, host=LOCALHOST, port=port, database=POSTGRES_ADMIN_ROLE)
    subprocess.run(
        [str(postgres_bin_dir / PG_CTL), "-D", str(data), "-m", "fast", "-w", "-t", str(STOP_TIMEOUT_S), "stop"],
        check=False,
        capture_output=True,
        text=True,
        timeout=STOP_TIMEOUT_S + COMMAND_TIMEOUT_S,
    )


@pytest.fixture
def postgres_dsn(postgres_server: str, postgres_bin_dir: Path) -> Iterator[str]:
    port = int(postgres_server.rsplit(":", 1)[1].split("/", 1)[0])
    database = DATABASE_PREFIX + uuid.uuid4().hex
    run_psql(postgres_bin_dir, port, POSTGRES_ADMIN_ROLE, f"CREATE DATABASE {database} OWNER {POSTGRES_APP_ROLE}")
    yield DSN_TEMPLATE.format(role=POSTGRES_APP_ROLE, host=LOCALHOST, port=port, database=database)
    run_psql(postgres_bin_dir, port, POSTGRES_ADMIN_ROLE, f"DROP DATABASE {database} WITH (FORCE)")
