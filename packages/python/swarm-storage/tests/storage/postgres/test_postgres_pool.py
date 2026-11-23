from __future__ import annotations

# Standard library imports
from typing import ClassVar
from uuid import UUID

# Third-party imports
import pytest
from pytest import MonkeyPatch

# First-party imports
from swarm_storage.models.config.postgres_config import PostgresConfig
from swarm_storage.models.postgres.exceptions import (
    SEStorageConnectionError,
    SEStorageDsnMissingError,
    SEStorageNotOpenError,
)
from swarm_storage.storage.postgres.postgres_pool import PostgresPool


class TestPostgresPool:
    OPERATOR_A: ClassVar[UUID] = UUID("01890a5d-ac96-774b-bcce-b302099a8057")
    CLOSED_PORT_DSN: ClassVar[str] = "postgresql://swarm_app:s3cret-pw@127.0.0.1:1/swarm"
    SECRET: ClassVar[str] = "s3cret-pw"
    DSN_SCHEME: ClassVar[str] = "postgresql://"

    async def test_open_without_the_environment_entry_is_refused(self, monkeypatch: MonkeyPatch) -> None:
        config = PostgresConfig()
        monkeypatch.delenv(config.dsn_key, raising=False)
        pool = PostgresPool(config)
        with pytest.raises(SEStorageDsnMissingError) as raised:
            await pool.open()
        assert self.SECRET not in str(raised.value)
        assert self.DSN_SCHEME not in str(raised.value)
        assert pool.is_open is False

    async def test_a_dsn_to_a_closed_port_is_refused_without_quoting_it(self, monkeypatch: MonkeyPatch) -> None:
        config = PostgresConfig()
        monkeypatch.setenv(config.dsn_key, self.CLOSED_PORT_DSN)
        pool = PostgresPool(config)
        with pytest.raises(SEStorageConnectionError) as raised:
            await pool.open()
        assert self.SECRET not in str(raised.value)
        assert pool.is_open is False

    async def test_is_open_follows_open_and_close(self, monkeypatch: MonkeyPatch, postgres_dsn: str) -> None:
        config = PostgresConfig()
        monkeypatch.setenv(config.dsn_key, postgres_dsn)
        pool = PostgresPool(config)
        assert pool.is_open is False
        await pool.open()
        assert pool.is_open is True
        await pool.close()
        assert pool.is_open is False

    async def test_close_before_open_is_safe(self) -> None:
        pool = PostgresPool(PostgresConfig())
        await pool.close()
        assert pool.is_open is False

    async def test_close_twice_is_safe(self, monkeypatch: MonkeyPatch, postgres_dsn: str) -> None:
        config = PostgresConfig()
        monkeypatch.setenv(config.dsn_key, postgres_dsn)
        pool = PostgresPool(config)
        await pool.open()
        await pool.close()
        await pool.close()
        assert pool.is_open is False

    async def test_a_unit_of_work_before_open_is_refused(self) -> None:
        pool = PostgresPool(PostgresConfig())
        with pytest.raises(SEStorageNotOpenError):
            pool.unit_of_work(self.OPERATOR_A)
