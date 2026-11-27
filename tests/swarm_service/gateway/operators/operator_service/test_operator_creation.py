from __future__ import annotations

# Standard library imports
from typing import List

# Third-party imports
import pytest

# First-party imports
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.keycloak.exceptions import SEKeycloakUnreachableError
from swarm_models.operators.exceptions import SEOperatorPlannerEmailTakenError
from swarm_models.people.enums import RoleName
from swarm_service.gateway.operators.operator_service import OperatorService
from swarm_storage.gateway.people.person_repository import PersonRepository
from swarm_storage.shared.postgres.postgres_pool import PostgresPool
from tests.fakes.keycloak.keycloak_admin_stand_in import KeycloakAdminStandIn
from tests.swarm_service.gateway.operators.operator_service.helpers import (
    ACTIONS_EMAIL_PATH,
    CELL,
    COUNT_CELL_ASSIGNMENTS,
    COUNT_OPERATORS,
    MEMBERS_PATH,
    OPERATOR_NAME,
    ORGANISATIONS_PATH,
    OTHER_OPERATOR_NAME,
    OTHER_PLANNER_EMAIL,
    PLANNER_EMAIL,
    PLANNER_NAME,
    ROLE_MAPPINGS_PATH,
    SCHEMA,
    USERS_PATH,
    an_entry,
    count_rows,
    operator_id_of,
)


class TestOperatorCreation:
    async def test_the_operator_is_stored_with_a_version_7_identifier(self, service: OperatorService) -> None:
        created = await service.create(an_entry())
        assert created.operator.name == OPERATOR_NAME
        assert created.operator.id.version == 7
        assert created.operator.deployment == Deployment.CLOUD
        assert created.operator.jurisdictions == [Jurisdiction.EU_EASA]
        assert await service.get(created.operator.id) == created.operator

    async def test_the_operator_is_assigned_to_the_configured_cell(self, service: OperatorService) -> None:
        created = await service.create(an_entry())
        assert created.cell_assignment.operator_id == created.operator.id
        assert created.cell_assignment.cell == CELL

    async def test_the_first_mission_planner_belongs_to_the_operator(self, service: OperatorService) -> None:
        created = await service.create(an_entry())
        assert created.first_mission_planner.operator_id == created.operator.id
        assert created.first_mission_planner.name == PLANNER_NAME
        assert created.first_mission_planner.email == PLANNER_EMAIL

    async def test_a_planner_without_a_name_is_named_after_her_email(self, service: OperatorService) -> None:
        created = await service.create(an_entry(planner_name=None))
        assert created.first_mission_planner.name == PLANNER_EMAIL

    @pytest.mark.parametrize(
        "deployment, expected",
        [(Deployment.CLOUD, LlmProvider.CLAUDE), (Deployment.ON_PREMISES, LlmProvider.OPEN_WEIGHT)],
    )
    async def test_the_llm_provider_follows_the_deployment_by_default(
        self, service: OperatorService, deployment: Deployment, expected: LlmProvider
    ) -> None:
        created = await service.create(an_entry(deployment=deployment))
        assert created.operator.llm_provider == expected

    async def test_an_llm_provider_in_the_entry_wins_over_the_default(self, service: OperatorService) -> None:
        created = await service.create(an_entry(deployment=Deployment.ON_PREMISES, llm_provider=LlmProvider.CLAUDE))
        assert created.operator.llm_provider == LlmProvider.CLAUDE

    async def test_anchoring_is_qualified_timestamping_by_default(self, service: OperatorService) -> None:
        created = await service.create(an_entry())
        assert created.operator.anchoring == Anchoring.QUALIFIED_TIMESTAMPING

    async def test_an_anchoring_in_the_entry_is_kept(self, service: OperatorService) -> None:
        created = await service.create(an_entry(anchoring=Anchoring.NONE))
        assert created.operator.anchoring == Anchoring.NONE

    async def test_every_jurisdiction_of_the_entry_is_kept(self, service: OperatorService) -> None:
        both: List[Jurisdiction] = [Jurisdiction.EU_EASA, Jurisdiction.US_FAA]
        created = await service.create(an_entry(jurisdictions=both))
        assert created.operator.jurisdictions == both

    async def test_the_keycloak_organisation_and_the_invited_planner_are_created(
        self, service: OperatorService, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        created = await service.create(an_entry())
        assert len(keycloak_admin_stand_in.organisations) == 1
        assert len(keycloak_admin_stand_in.users) == 1
        organisation_id, organisation = next(iter(keycloak_admin_stand_in.organisations.items()))
        user_id, user = next(iter(keycloak_admin_stand_in.users.items()))
        assert OPERATOR_NAME in str(organisation)
        assert user["email"] == PLANNER_EMAIL
        assert operator_id_of(user) == created.operator.id
        assert keycloak_admin_stand_in.realm_roles[user_id] == [RoleName.MISSION_PLANNER.value]
        assert keycloak_admin_stand_in.members[organisation_id] == [user_id]

    async def test_one_actions_email_invites_the_planner(
        self, service: OperatorService, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        await service.create(an_entry())
        user_id = next(iter(keycloak_admin_stand_in.users))
        assert [sent[0] for sent in keycloak_admin_stand_in.action_emails] == [user_id]

    async def test_an_email_keycloak_knows_is_refused_and_nothing_is_left(
        self, service: OperatorService, keycloak_admin_stand_in: KeycloakAdminStandIn, postgres_dsn: str
    ) -> None:
        keycloak_admin_stand_in.existing_email(PLANNER_EMAIL)
        known_users = len(keycloak_admin_stand_in.users)
        with pytest.raises(SEOperatorPlannerEmailTakenError):
            await service.create(an_entry())
        assert keycloak_admin_stand_in.organisations == {}
        assert len(keycloak_admin_stand_in.users) == known_users
        assert await count_rows(postgres_dsn, COUNT_OPERATORS) == 0
        assert await count_rows(postgres_dsn, COUNT_CELL_ASSIGNMENTS) == 0

    async def test_the_name_stays_free_after_an_email_was_refused(
        self, service: OperatorService, keycloak_admin_stand_in: KeycloakAdminStandIn
    ) -> None:
        keycloak_admin_stand_in.existing_email(PLANNER_EMAIL)
        with pytest.raises(SEOperatorPlannerEmailTakenError):
            await service.create(an_entry())
        created = await service.create(an_entry(planner_email=OTHER_PLANNER_EMAIL))
        assert created.operator.name == OPERATOR_NAME

    @pytest.mark.parametrize(
        "fragment", [ORGANISATIONS_PATH, USERS_PATH, ROLE_MAPPINGS_PATH, MEMBERS_PATH, ACTIONS_EMAIL_PATH]
    )
    async def test_a_keycloak_failure_leaves_no_row_and_no_keycloak_object(
        self,
        service: OperatorService,
        keycloak_admin_stand_in: KeycloakAdminStandIn,
        postgres_dsn: str,
        fragment: str,
    ) -> None:
        keycloak_admin_stand_in.fail_path(fragment)
        with pytest.raises(SEKeycloakUnreachableError):
            await service.create(an_entry())
        assert keycloak_admin_stand_in.organisations == {}
        assert keycloak_admin_stand_in.users == {}
        assert await count_rows(postgres_dsn, COUNT_OPERATORS) == 0
        assert await count_rows(postgres_dsn, COUNT_CELL_ASSIGNMENTS) == 0

    async def test_the_person_of_each_operator_is_visible_only_to_her_operator(
        self, service: OperatorService, reading_pool: PostgresPool
    ) -> None:
        first = await service.create(an_entry())
        second = await service.create(an_entry(name=OTHER_OPERATOR_NAME, planner_email=OTHER_PLANNER_EMAIL))
        async with reading_pool.unit_of_work(first.operator.id) as uow:
            visible = await PersonRepository(uow, SCHEMA).list()
            assert [person.id for person in visible] == [first.first_mission_planner.id]
            assert await PersonRepository(uow, SCHEMA).get(second.first_mission_planner.id) is None
        async with reading_pool.unit_of_work(second.operator.id) as uow:
            visible = await PersonRepository(uow, SCHEMA).list()
            assert [person.id for person in visible] == [second.first_mission_planner.id]
            assert await PersonRepository(uow, SCHEMA).get(first.first_mission_planner.id) is None

    async def test_no_person_is_visible_without_an_operator(
        self, service: OperatorService, reading_pool: PostgresPool
    ) -> None:
        await service.create(an_entry())
        async with reading_pool.unit_of_work(None) as uow:
            assert await PersonRepository(uow, SCHEMA).list() == []

    async def test_the_identifiers_of_two_operators_differ(self, service: OperatorService) -> None:
        first = await service.create(an_entry())
        second = await service.create(an_entry(name=OTHER_OPERATOR_NAME, planner_email=OTHER_PLANNER_EMAIL))
        assert first.operator.id != second.operator.id
