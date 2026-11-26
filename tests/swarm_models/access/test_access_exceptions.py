from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest

# First-party imports
from swarm_models.access.exceptions import (
    SEAccessError,
    SEAccessExpiredTokenError,
    SEAccessInvalidTokenError,
    SEAccessMissingRoleError,
    SEAccessMissingTokenError,
    SEAccessWrongOperatorError,
)
from swarm_models.enums import AccessRefusal


class TestAccessErrors:
    REFUSALS: ClassVar[Dict[type[SEAccessError], AccessRefusal]] = {
        SEAccessMissingTokenError: AccessRefusal.MISSING_TOKEN,
        SEAccessInvalidTokenError: AccessRefusal.INVALID_TOKEN,
        SEAccessExpiredTokenError: AccessRefusal.EXPIRED_TOKEN,
        SEAccessWrongOperatorError: AccessRefusal.WRONG_OPERATOR,
        SEAccessMissingRoleError: AccessRefusal.MISSING_ROLE,
    }
    MESSAGE: ClassVar[str] = "The call is refused."

    @pytest.mark.parametrize("error", list(REFUSALS))
    def test_each_error_is_an_access_error(self, error: type[SEAccessError]) -> None:
        assert issubclass(error, SEAccessError)
        assert issubclass(error, Exception)

    @pytest.mark.parametrize("error", list(REFUSALS))
    def test_each_error_carries_its_refusal(self, error: type[SEAccessError]) -> None:
        assert error.REFUSAL is self.REFUSALS[error]
        assert error(self.MESSAGE).REFUSAL is self.REFUSALS[error]

    @pytest.mark.parametrize("error", list(REFUSALS))
    def test_each_error_keeps_its_message(self, error: type[SEAccessError]) -> None:
        assert str(error(self.MESSAGE)) == self.MESSAGE

    @pytest.mark.parametrize("error", list(REFUSALS))
    def test_each_error_chains_its_cause(self, error: type[SEAccessError]) -> None:
        cause = ValueError("root cause")
        with pytest.raises(error) as caught:
            try:
                raise cause
            except ValueError as inner:
                raise error(self.MESSAGE) from inner
        assert caught.value.__cause__ is cause

    @pytest.mark.parametrize("error", list(REFUSALS))
    def test_a_base_handler_catches_each_error(self, error: type[SEAccessError]) -> None:
        with pytest.raises(SEAccessError):
            raise error(self.MESSAGE)

    def test_the_refusals_are_all_different(self) -> None:
        assert len(set(self.REFUSALS.values())) == len(self.REFUSALS)
