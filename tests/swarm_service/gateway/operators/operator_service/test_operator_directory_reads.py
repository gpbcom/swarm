from __future__ import annotations

# Standard library imports
from typing import ClassVar, Tuple
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_models.operators.exceptions import SEOperatorNotFoundError
from swarm_service.gateway.operators.operator_service import OperatorService
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn
from tests.swarm_service.gateway.operators.operator_service.helpers import CELL, a_pool, a_service, an_entry


class TestOperatorDirectoryReads:
    MISSING: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e7f")
    NAMES: ClassVar[Tuple[str, ...]] = ("Aerowing Services", "Borealis Drones", "Cirrus Survey")
    EMAIL_TEMPLATE: ClassVar[str] = "planner{number}@example.org"

    async def create_three(self, service: OperatorService) -> None:
        for number, name in enumerate(self.NAMES):
            await service.create(an_entry(name=name, planner_email=self.EMAIL_TEMPLATE.format(number=number)))

    async def test_an_empty_directory_lists_nothing(self, service: OperatorService) -> None:
        assert await service.list() == []

    async def test_the_directory_lists_the_operators_in_identifier_order(self, service: OperatorService) -> None:
        await self.create_three(service)
        identifiers = [entry.operator.id for entry in await service.list()]
        assert len(identifiers) == len(self.NAMES)
        assert identifiers == sorted(identifiers)

    async def test_each_entry_carries_the_cell_assignment_of_its_operator(self, service: OperatorService) -> None:
        await self.create_three(service)
        for entry in await service.list():
            assert entry.cell_assignment.operator_id == entry.operator.id
            assert entry.cell_assignment.cell == CELL

    async def test_the_directory_is_read_page_by_page(self, service: OperatorService) -> None:
        await self.create_three(service)
        everything = [entry.operator.id for entry in await service.list()]
        first = await service.list(limit=2)
        second = await service.list(after=first[-1].operator.id, limit=2)
        assert [entry.operator.id for entry in first + second] == everything

    async def test_get_returns_the_operator(self, service: OperatorService) -> None:
        created = await service.create(an_entry())
        assert await service.get(created.operator.id) == created.operator

    async def test_an_unknown_operator_is_not_found(self, service: OperatorService) -> None:
        with pytest.raises(SEOperatorNotFoundError):
            await service.get(self.MISSING)

    async def test_closing_a_service_that_was_never_used_is_safe(
        self, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        unused = a_service(a_pool(), keycloak_admin_stand_in)
        await unused.close()

    async def test_closing_twice_is_safe(self, service: OperatorService) -> None:
        await service.list()
        await service.close()
        await service.close()
