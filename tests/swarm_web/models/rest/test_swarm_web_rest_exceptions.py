from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from inspect import isclass
from typing import ClassVar, Dict, List, Type

# Third-party imports
import pytest

# First-party imports
from swarm_rest.models.rest import exceptions
from swarm_rest.models.rest.exceptions import (
    SEIdempotencyKeyInFlightError,
    SEIdempotencyKeyInvalidError,
    SEIdempotencyKeyMissingError,
    SEIdempotencyKeyReusedError,
    SEPreconditionFailedError,
    SEPreconditionRequiredError,
    SERestError,
    SERestServerStartError,
)


class TestSwarmRestErrors:
    STATUSES: ClassVar[Dict[Type[SERestError], int]] = {
        SEIdempotencyKeyMissingError: 400,
        SEIdempotencyKeyInvalidError: 400,
        SEIdempotencyKeyReusedError: 422,
        SEIdempotencyKeyInFlightError: 409,
        SEPreconditionRequiredError: 428,
        SEPreconditionFailedError: 412,
        SERestServerStartError: 500,
    }
    SUBCLASSES: ClassVar[List[Type[SERestError]]] = list(STATUSES)
    BASE_STATUS: ClassVar[int] = 500

    def test_the_base_error_is_an_internal_server_error(self) -> None:
        assert SERestError.STATUS == self.BASE_STATUS
        assert SERestError.TITLE == HTTPStatus(self.BASE_STATUS).phrase

    def test_the_base_error_is_an_exception(self) -> None:
        assert issubclass(SERestError, Exception)

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_every_error_is_a_rest_error(self, error: Type[SERestError]) -> None:
        assert issubclass(error, SERestError)

    @pytest.mark.parametrize(("error", "status"), list(STATUSES.items()))
    def test_every_error_has_its_status(self, error: Type[SERestError], status: int) -> None:
        assert error.STATUS == status

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_the_title_is_the_phrase_of_the_status(self, error: Type[SERestError]) -> None:
        assert error.TITLE == HTTPStatus(error.STATUS).phrase

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_an_error_keeps_its_message(self, error: Type[SERestError]) -> None:
        assert str(error("Something went wrong.")) == "Something went wrong."

    def test_all_is_sorted(self) -> None:
        assert exceptions.__all__ == sorted(exceptions.__all__)

    def test_all_is_complete(self) -> None:
        defined = {name for name, value in vars(exceptions).items() if isclass(value) and name.startswith("SE")}
        assert set(exceptions.__all__) == defined
        assert defined >= {error.__name__ for error in [SERestError, *self.SUBCLASSES]}
