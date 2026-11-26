from __future__ import annotations

# Standard library imports
from typing import AsyncIterator, ClassVar
from uuid import UUID

# Third-party imports
import asyncpg
import pytest
from pytest import MonkeyPatch

# First-party imports
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_models.storage.exceptions import SEStorageNotOpenError
from swarm_storage.shared.postgres.postgres_pool import PostgresPool
from swarm_storage.shared.postgres.unit_of_work import UnitOfWork


class TestUnitOfWork:
    OPERATOR_A: ClassVar[UUID] = UUID("01890a5d-ac96-774b-bcce-b302099a8057")
    SETTING_QUERY: ClassVar[str] = "SELECT current_setting($1, true)"
    CREATE_PROBE: ClassVar[str] = "CREATE TABLE public.uow_probe (id integer primary key)"
    INSERT_PROBE: ClassVar[str] = "INSERT INTO public.uow_probe (id) VALUES (1)"
    COUNT_PROBE: ClassVar[str] = "SELECT count(*) FROM public.uow_probe"

    @pytest.fixture
    async def pool(self, monkeypatch: MonkeyPatch, postgres_dsn: str) -> AsyncIterator[PostgresPool]:
        monkeypatch.setenv(PostgresConfig().dsn_key, postgres_dsn)
        opened = PostgresPool(PostgresConfig())
        await opened.open()
        yield opened
        await opened.close()

    @pytest.fixture
    async def single_pool(self, monkeypatch: MonkeyPatch, postgres_dsn: str) -> AsyncIterator[PostgresPool]:
        monkeypatch.setenv(PostgresConfig().dsn_key, postgres_dsn)
        opened = PostgresPool(PostgresConfig(pool_min_size=1, pool_max_size=1))
        await opened.open()
        yield opened
        await opened.close()

    @pytest.fixture
    async def raw(self, postgres_dsn: str) -> AsyncIterator[asyncpg.Connection]:
        connection = await asyncpg.connect(postgres_dsn)
        yield connection
        await connection.close()

    async def test_the_operator_is_set_for_the_transaction(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            value = await uow.connection.fetchval(self.SETTING_QUERY, UnitOfWork.OPERATOR_SETTING)
            assert value == str(self.OPERATOR_A)
            assert uow.operator_id == self.OPERATOR_A

    async def test_without_an_operator_the_setting_is_empty(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(None) as uow:
            value = await uow.connection.fetchval(self.SETTING_QUERY, UnitOfWork.OPERATOR_SETTING)
            assert not value

    async def test_the_setting_never_leaks_into_the_next_unit_of_work(self, single_pool: PostgresPool) -> None:
        async with single_pool.unit_of_work(self.OPERATOR_A):
            pass
        async with single_pool.unit_of_work(None) as uow:
            value = await uow.connection.fetchval(self.SETTING_QUERY, UnitOfWork.OPERATOR_SETTING)
            assert not value

    async def test_the_work_commits_on_a_normal_exit(self, pool: PostgresPool, raw: asyncpg.Connection) -> None:
        await raw.execute(self.CREATE_PROBE)
        async with pool.unit_of_work(self.OPERATOR_A) as uow:
            await uow.connection.execute(self.INSERT_PROBE)
        assert await raw.fetchval(self.COUNT_PROBE) == 1

    async def test_an_exception_rolls_back_and_propagates(self, pool: PostgresPool, raw: asyncpg.Connection) -> None:
        await raw.execute(self.CREATE_PROBE)
        with pytest.raises(ZeroDivisionError):
            async with pool.unit_of_work(self.OPERATOR_A) as uow:
                await uow.connection.execute(self.INSERT_PROBE)
                raise ZeroDivisionError
        assert await raw.fetchval(self.COUNT_PROBE) == 0

    async def test_the_connection_outside_the_block_is_refused(self, pool: PostgresPool) -> None:
        uow = pool.unit_of_work(self.OPERATOR_A)
        with pytest.raises(SEStorageNotOpenError):
            assert uow.connection
        async with uow:
            pass
        with pytest.raises(SEStorageNotOpenError):
            assert uow.connection
