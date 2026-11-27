from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, Type

# Third-party imports
import pytest

# First-party imports
from swarm_models.operators.exceptions import (
    SEOperatorFieldMissingError,
    SEOperatorNameTakenError,
    SEOperatorNotFoundError,
    SEOperatorPlannerEmailTakenError,
)
from swarm_web.models.rest.exceptions import SERestError


class TestRestOperator:
    STATUSES: ClassVar[Dict[Type[SERestError], int]] = {
        SEOperatorFieldMissingError: 422,
        SEOperatorNameTakenError: 409,
        SEOperatorPlannerEmailTakenError: 409,
        SEOperatorNotFoundError: 404,
    }

    @pytest.mark.parametrize("error", list(STATUSES))
    def test_each_refusal_is_a_rest_error(self, error: Type[SERestError]) -> None:
        assert issubclass(error, SERestError)

    @pytest.mark.parametrize("error", list(STATUSES))
    def test_each_refusal_has_its_http_status(self, error: Type[SERestError]) -> None:
        assert error.STATUS == self.STATUSES[error]
