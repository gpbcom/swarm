from __future__ import annotations

# Standard library imports
from typing import ClassVar, List

# Third-party imports
import pytest

# First-party imports
from gateway.models.access.exceptions import SEAccessError
from gateway.models.enums import AccessRefusal
from gateway.models.keycloak.exceptions import (
    SEKeycloakError,
    SEKeycloakUnknownKeyError,
    SEKeycloakUnreachableError,
)


class TestKeycloakErrors:
    SUBCLASSES: ClassVar[List[type[SEKeycloakError]]] = [SEKeycloakUnreachableError, SEKeycloakUnknownKeyError]
    MESSAGE: ClassVar[str] = "The identity provider failed."

    def test_the_base_refusal_is_identity_unavailable(self) -> None:
        assert SEKeycloakError.REFUSAL is AccessRefusal.IDENTITY_UNAVAILABLE

    def test_the_base_is_not_an_access_error(self) -> None:
        assert not issubclass(SEKeycloakError, SEAccessError)

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_each_error_is_a_keycloak_error(self, error: type[SEKeycloakError]) -> None:
        assert issubclass(error, SEKeycloakError)
        assert not issubclass(error, SEAccessError)

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_each_error_carries_its_refusal(self, error: type[SEKeycloakError]) -> None:
        assert error.REFUSAL is AccessRefusal.IDENTITY_UNAVAILABLE
        assert error(self.MESSAGE).REFUSAL is AccessRefusal.IDENTITY_UNAVAILABLE

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_each_error_keeps_its_message(self, error: type[SEKeycloakError]) -> None:
        assert str(error(self.MESSAGE)) == self.MESSAGE

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_each_error_chains_its_cause(self, error: type[SEKeycloakError]) -> None:
        cause = OSError("connection refused")
        with pytest.raises(error) as caught:
            try:
                raise cause
            except OSError as inner:
                raise error(self.MESSAGE) from inner
        assert caught.value.__cause__ is cause
