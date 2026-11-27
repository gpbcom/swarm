from __future__ import annotations

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import OperatorField
from swarm_models.operators.exceptions import SEOperatorFieldMissingError, SEOperatorNameTakenError
from swarm_service.gateway.operators.operator_service import OperatorService
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn
from tests.swarm_service.gateway.operators.operator_service.helpers import (
    COUNT_CELL_ASSIGNMENTS,
    COUNT_OPERATORS,
    OPERATOR_NAME,
    OTHER_PLANNER_EMAIL,
    an_entry,
    count_rows,
)


class TestOperatorEntryChecks:
    async def test_a_missing_name_is_named_in_the_refusal(self, service: OperatorService) -> None:
        with pytest.raises(SEOperatorFieldMissingError, match=OperatorField.NAME.value):
            await service.create(an_entry(name=None))

    async def test_a_missing_deployment_is_named_in_the_refusal(self, service: OperatorService) -> None:
        with pytest.raises(SEOperatorFieldMissingError, match=OperatorField.DEPLOYMENT.value):
            await service.create(an_entry(deployment=None))

    async def test_a_missing_jurisdiction_is_named_in_the_refusal(self, service: OperatorService) -> None:
        with pytest.raises(SEOperatorFieldMissingError, match=OperatorField.JURISDICTIONS.value):
            await service.create(an_entry(jurisdictions=[]))

    async def test_a_missing_planner_email_is_named_in_the_refusal(self, service: OperatorService) -> None:
        with pytest.raises(SEOperatorFieldMissingError, match=OperatorField.FIRST_MISSION_PLANNER_EMAIL.value):
            await service.create(an_entry(planner_email=None))

    async def test_every_missing_field_is_named_at_once(self, service: OperatorService) -> None:
        with pytest.raises(SEOperatorFieldMissingError) as refusal:
            await service.create(an_entry(name=None, deployment=None, jurisdictions=[], planner_email=None))
        for field in OperatorField:
            assert field.value in str(refusal.value)

    async def test_a_missing_field_is_reported_before_a_name_taken(self, service: OperatorService) -> None:
        await service.create(an_entry())
        with pytest.raises(SEOperatorFieldMissingError):
            await service.create(an_entry(planner_email=None))

    async def test_a_missing_field_stores_nothing_and_calls_keycloak_not_at_all(
        self, service: OperatorService, keycloak_admin_stand_in: KeycloakAdminStandIn, postgres_dsn: str
    ) -> None:
        with pytest.raises(SEOperatorFieldMissingError):
            await service.create(an_entry(deployment=None))
        assert await count_rows(postgres_dsn, COUNT_OPERATORS) == 0
        assert await count_rows(postgres_dsn, COUNT_CELL_ASSIGNMENTS) == 0
        assert keycloak_admin_stand_in.organisations == {}
        assert keycloak_admin_stand_in.users == {}
        assert keycloak_admin_stand_in.action_emails == []

    @pytest.mark.parametrize(
        "name", [OPERATOR_NAME, OPERATOR_NAME.upper(), OPERATOR_NAME.lower(), f"  {OPERATOR_NAME}  "]
    )
    async def test_a_name_that_exists_is_refused_whatever_its_case_or_spaces(
        self, service: OperatorService, name: str
    ) -> None:
        await service.create(an_entry())
        with pytest.raises(SEOperatorNameTakenError):
            await service.create(an_entry(name=name, planner_email=OTHER_PLANNER_EMAIL))

    async def test_a_name_taken_stores_nothing_more_and_calls_keycloak_no_more(
        self, service: OperatorService, keycloak_admin_stand_in: KeycloakAdminStandIn, postgres_dsn: str
    ) -> None:
        await service.create(an_entry())
        with pytest.raises(SEOperatorNameTakenError):
            await service.create(an_entry(name=OPERATOR_NAME.upper(), planner_email=OTHER_PLANNER_EMAIL))
        assert await count_rows(postgres_dsn, COUNT_OPERATORS) == 1
        assert await count_rows(postgres_dsn, COUNT_CELL_ASSIGNMENTS) == 1
        assert len(keycloak_admin_stand_in.organisations) == 1
        assert len(keycloak_admin_stand_in.users) == 1
        assert len(keycloak_admin_stand_in.action_emails) == 1
