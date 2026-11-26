from __future__ import annotations

# Standard library imports
import logging
from typing import List, Optional, Type
from uuid import UUID, uuid4

# Third-party imports
import pytest

# First-party imports
from gateway.models.access.exceptions import SEAccessError, SEAccessMissingRoleError, SEAccessWrongOperatorError
from gateway.models.auth.caller import Caller
from gateway.models.enums import AccessRefusal
from gateway.service.auth.access_guard import AccessGuard
from swarm_models.models.people.enums import RoleName


class TestAccessGuard:
    def caller(self, operator_id: Optional[UUID], roles: List[RoleName]) -> Caller:
        return Caller(person_id=uuid4(), operator_id=operator_id, roles=roles)

    def test_the_right_operator_and_role_pass(self) -> None:
        operator_id = uuid4()
        caller = self.caller(operator_id, [RoleName.PILOT, RoleName.MISSION_PLANNER])
        assert AccessGuard().check(caller, [RoleName.PILOT], operator_id) is None

    def test_a_missing_operator_checks_the_role_only(self) -> None:
        caller = self.caller(uuid4(), [RoleName.PILOT])
        assert AccessGuard().check(caller, [RoleName.PILOT], None) is None

    def test_a_swarm_administrator_passes_without_an_operator(self) -> None:
        caller = self.caller(None, [RoleName.SWARM_ADMINISTRATOR])
        assert AccessGuard().check(caller, [RoleName.SWARM_ADMINISTRATOR], None) is None

    @pytest.mark.parametrize(
        "caller_roles, required",
        [
            ([RoleName.PILOT], [RoleName.PILOT]),
            ([RoleName.PILOT], [RoleName.MISSION_PLANNER]),
            ([RoleName.PILOT], []),
        ],
    )
    def test_another_operators_id_is_refused_whatever_the_role(
        self, caller_roles: List[RoleName], required: List[RoleName]
    ) -> None:
        caller = self.caller(uuid4(), caller_roles)
        with pytest.raises(SEAccessWrongOperatorError) as raised:
            AccessGuard().check(caller, required, uuid4())
        assert raised.value.REFUSAL is AccessRefusal.WRONG_OPERATOR

    def test_a_swarm_administrator_naming_an_operator_is_refused(self) -> None:
        caller = self.caller(None, [RoleName.SWARM_ADMINISTRATOR])
        with pytest.raises(SEAccessWrongOperatorError):
            AccessGuard().check(caller, [RoleName.SWARM_ADMINISTRATOR], uuid4())

    @pytest.mark.parametrize(
        "caller_roles, required",
        [
            ([RoleName.PILOT], [RoleName.MISSION_PLANNER]),
            ([RoleName.PILOT, RoleName.CLIENT], [RoleName.INSTRUCTOR, RoleName.SITE_AGENT]),
            ([], [RoleName.PILOT]),
            ([RoleName.PILOT], []),
        ],
    )
    def test_no_common_role_is_refused(self, caller_roles: List[RoleName], required: List[RoleName]) -> None:
        operator_id = uuid4()
        caller = self.caller(operator_id, caller_roles)
        with pytest.raises(SEAccessMissingRoleError) as raised:
            AccessGuard().check(caller, required, operator_id)
        assert raised.value.REFUSAL is AccessRefusal.MISSING_ROLE

    def test_a_missing_operator_still_refuses_a_missing_role(self) -> None:
        caller = self.caller(uuid4(), [RoleName.PILOT])
        with pytest.raises(SEAccessMissingRoleError):
            AccessGuard().check(caller, [RoleName.INSTRUCTOR], None)

    @pytest.mark.parametrize(
        "same_operator, roles, error",
        [
            (False, [RoleName.PILOT], SEAccessWrongOperatorError),
            (False, [RoleName.INSTRUCTOR], SEAccessWrongOperatorError),
            (True, [RoleName.INSTRUCTOR], SEAccessMissingRoleError),
        ],
    )
    def test_each_refusal_logs_one_error(
        self,
        caplog: pytest.LogCaptureFixture,
        same_operator: bool,
        roles: List[RoleName],
        error: Type[SEAccessError],
    ) -> None:
        operator_id = uuid4()
        caller = self.caller(operator_id, [RoleName.PILOT])
        named = operator_id if same_operator else uuid4()
        with caplog.at_level(logging.DEBUG), pytest.raises(error):
            AccessGuard().check(caller, roles, named)
        errors = [record for record in caplog.records if record.levelno == logging.ERROR]
        assert len(errors) == 1

    def test_a_pass_logs_no_error(self, caplog: pytest.LogCaptureFixture) -> None:
        operator_id = uuid4()
        caller = self.caller(operator_id, [RoleName.PILOT])
        with caplog.at_level(logging.DEBUG):
            AccessGuard().check(caller, [RoleName.PILOT], operator_id)
        assert [record for record in caplog.records if record.levelno >= logging.ERROR] == []
