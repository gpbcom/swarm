from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime
from typing import AsyncIterator, ClassVar
from uuid import UUID

# Third-party imports
import asyncpg
import pytest

# First-party imports
from swarm_models.config.postgres.postgres_config import PostgresConfig
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.gateway.operators.cell_assignment_repository import CellAssignmentRepository
from swarm_storage.shared.postgres.postgres_pool import PostgresPool


class TestCellAssignmentRepository:
    SCHEMA: ClassVar[str] = "directory"
    SETUP_SCHEMA: ClassVar[str] = "CREATE SCHEMA directory"
    OPERATOR_A: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60")
    OPERATOR_B: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61")
    MISSING: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e7f")
    CELL: ClassVar[str] = "eu-west"
    ASSIGNED_AT: ClassVar[datetime] = datetime(2026, 11, 27, 9, 30, 15, 123456, tzinfo=UTC)

    @pytest.fixture
    async def pool(self, monkeypatch: pytest.MonkeyPatch, postgres_dsn: str) -> AsyncIterator[PostgresPool]:
        config = PostgresConfig()
        monkeypatch.setenv(config.dsn_key, postgres_dsn)
        connection = await asyncpg.connect(postgres_dsn)
        await connection.execute(self.SETUP_SCHEMA)
        for statement in OperatorDirectoryTables().create(self.SCHEMA):
            await connection.execute(statement)
        await connection.close()
        pool = PostgresPool(config)
        await pool.open()
        yield pool
        await pool.close()

    def assignment(self, operator_id: UUID) -> CellAssignment:
        return CellAssignment(operator_id=operator_id, cell=self.CELL, assigned_at=self.ASSIGNED_AT)

    async def test_an_assignment_round_trips_by_its_operator(self, pool: PostgresPool) -> None:
        assignment = self.assignment(self.OPERATOR_A)
        async with pool.unit_of_work(None) as uow:
            repository = CellAssignmentRepository(uow, self.SCHEMA)
            assert await repository.add(assignment) == assignment
            assert await repository.get(self.OPERATOR_A) == assignment

    async def test_an_operator_without_an_assignment_is_not_found(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(None) as uow:
            assert await CellAssignmentRepository(uow, self.SCHEMA).get(self.MISSING) is None

    async def test_list_returns_every_assignment_ordered_by_operator(self, pool: PostgresPool) -> None:
        async with pool.unit_of_work(None) as uow:
            repository = CellAssignmentRepository(uow, self.SCHEMA)
            await repository.add(self.assignment(self.OPERATOR_B))
            await repository.add(self.assignment(self.OPERATOR_A))
            listed = await repository.list()
        assert [item.operator_id for item in listed] == [self.OPERATOR_A, self.OPERATOR_B]
