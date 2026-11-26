from __future__ import annotations

# Standard library imports
import asyncio
import json
import socket
import time
import urllib.request
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

# Third-party imports
import nats
from nats.errors import Error as NatsError

# First-party imports
from swarm_nats.clients.account_resolver_client import AccountResolverClient
from swarm_nats.models.accounts.issued_account import IssuedAccount
from swarm_nats.models.accounts.issued_credential import IssuedCredential
from swarm_nats.models.accounts.issued_operator import IssuedOperator
from swarm_nats.service.accounts.account_issuer import AccountIssuer
from swarm_nats.service.accounts.credential_issuer import CredentialIssuer
from swarm_nats.service.accounts.nats_jwt_signer import NatsJwtSigner
from swarm_nats.service.accounts.nkey_factory import NkeyFactory
from swarm_nats.service.accounts.operator_issuer import OperatorIssuer

OPERATOR_A_ID = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7b")
OPERATOR_B_ID = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f6a7c")
CONNECT_TIMEOUT_S = 2.0
POLL_INTERVAL_S = 0.1
VIOLATION_TEXT = "permissions violation"
POLL_INTERVAL_S = 0.1
VIOLATION_TEXT = "permissions violation"
CREDS_MODE = 0o600
CONNZ_URL = "http://127.0.0.1:{port}/connz?auth=true"
CONNZ_CONNECTIONS_KEY = "connections"
CONNZ_USER_KEY = "authorized_user"
HOST = "127.0.0.1"
ENCODING = "utf-8"
COMMON_HEAD = """server_name: {server_name}
host: 127.0.0.1
port: {port}
http_port: {monitor_port}
operator: {operator_jwt}
system_account: {system_account}
"""
PRELOAD_ENTRY = '  {key}: "{jwt}"\n'
MEMORY_RESOLVER = "resolver: MEMORY\nresolver_preload: {{\n{entries}}}\n"
FULL_RESOLVER = 'resolver {{\n  type: full\n  dir: "{resolver_dir}"\n}}\nresolver_preload: {{\n{entries}}}\n'
JETSTREAM_BLOCK = 'jetstream {{\n  store_dir: "{store_dir}"\n{domain}}}\n'
JETSTREAM_DOMAIN = "  domain: {domain}\n"
LEAFNODES_BLOCK = "leafnodes {{\n  host: 127.0.0.1\n  port: {port}\n  no_advertise: true\n}}\n"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def issuers() -> Tuple[OperatorIssuer, AccountIssuer, CredentialIssuer]:
    return (
        OperatorIssuer(NkeyFactory(), NatsJwtSigner()),
        AccountIssuer(NkeyFactory(), NatsJwtSigner()),
        CredentialIssuer(NkeyFactory(), NatsJwtSigner()),
    )


def preload_entries(accounts: List[IssuedAccount]) -> str:
    return "".join(PRELOAD_ENTRY.format(key=account.public_key, jwt=account.jwt) for account in accounts)


def common_head(port: int, monitor_port: int, operator: IssuedOperator, server_name: str) -> str:
    return COMMON_HEAD.format(
        server_name=server_name,
        port=port,
        monitor_port=monitor_port,
        operator_jwt=operator.jwt,
        system_account=operator.system_account.public_key,
    )


def operator_mode_config(
    port: int,
    monitor_port: int,
    operator: IssuedOperator,
    accounts: List[IssuedAccount],
    store_dir: Optional[Path] = None,
    domain: Optional[str] = None,
    leafnode_port: Optional[int] = None,
    server_name: str = "cell",
) -> str:
    config = common_head(port, monitor_port, operator, server_name)
    config += MEMORY_RESOLVER.format(entries=preload_entries([operator.system_account, *accounts]))
    if store_dir is not None:
        domain_line = ""
        if domain is not None:
            domain_line = JETSTREAM_DOMAIN.format(domain=domain)
        config += JETSTREAM_BLOCK.format(store_dir=store_dir, domain=domain_line)
    if leafnode_port is not None:
        config += LEAFNODES_BLOCK.format(port=leafnode_port)
    return config


def full_resolver_config(port: int, monitor_port: int, operator: IssuedOperator, resolver_dir: Path) -> str:
    config = common_head(port, monitor_port, operator, "cell")
    config += FULL_RESOLVER.format(resolver_dir=resolver_dir, entries=preload_entries([operator.system_account]))
    return config


def write_creds(directory: Path, credential: IssuedCredential, issuer: CredentialIssuer) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{credential.name}.creds"
    path.write_text(issuer.creds_file(credential), encoding=ENCODING)
    path.chmod(CREDS_MODE)
    return path


async def connects(url: str, creds: Path) -> bool:
    """Tell whether the server accepts a new connection with these credentials."""
    try:
        client = await nats.connect(
            url,
            user_credentials=str(creds),
            allow_reconnect=False,
            connect_timeout=CONNECT_TIMEOUT_S,
        )
    except (NatsError, OSError):
        return False
    await client.close()
    return True


async def violation_seen(errors: List[Exception], timeout_s: float) -> bool:
    """Wait until the error callback has received a permissions violation, or the timeout passes."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        for error in errors:
            if VIOLATION_TEXT in str(error).lower():
                return True
        await asyncio.sleep(POLL_INTERVAL_S)
    return False


async def becomes_refused(url: str, creds: Path, timeout_s: float) -> bool:
    """Wait until the server refuses a new connection with these credentials, or the timeout passes."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if not await connects(url, creds):
            return True
        await asyncio.sleep(POLL_INTERVAL_S)
    return False


async def push_account(url: str, system_creds: Path, account: IssuedAccount, timeout_s: float) -> None:
    """Push an account to the resolver through a system connection."""
    system = await nats.connect(url, user_credentials=str(system_creds))
    await AccountResolverClient(system, timeout_s).push(account)
    await system.close()


def connz_users(monitor_port: int) -> List[str]:
    """Return the ``authorized_user`` of every connection the monitoring endpoint lists."""
    with urllib.request.urlopen(CONNZ_URL.format(port=monitor_port), timeout=CONNECT_TIMEOUT_S) as response:
        body = json.loads(response.read().decode(ENCODING))
    users: List[str] = []
    for connection in body[CONNZ_CONNECTIONS_KEY]:
        users.append(connection[CONNZ_USER_KEY])
    return users
