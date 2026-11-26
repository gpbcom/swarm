from __future__ import annotations

# Standard library imports
from typing import ClassVar, List

# Third-party imports
import pytest

# First-party imports
from swarm_models.storage import exceptions
from swarm_models.storage.exceptions import (
    SEStorageConnectionError,
    SEStorageDsnMissingError,
    SEStorageError,
    SEStorageInvalidIdentifierError,
    SEStorageInvalidPageError,
    SEStorageMigrationError,
    SEStorageNotOpenError,
    SEStorageOperatorRefusedError,
    SEStorageVersionConflictError,
)


class TestSwarmStorageErrors:
    SUBCLASSES: ClassVar[List[type[SEStorageError]]] = [
        SEStorageDsnMissingError,
        SEStorageConnectionError,
        SEStorageNotOpenError,
        SEStorageInvalidIdentifierError,
        SEStorageInvalidPageError,
        SEStorageVersionConflictError,
        SEStorageOperatorRefusedError,
        SEStorageMigrationError,
    ]

    @pytest.mark.parametrize("error", SUBCLASSES)
    def test_every_storage_error_subclasses_the_base(self, error: type[SEStorageError]) -> None:
        assert issubclass(error, SEStorageError)

    def test_the_base_is_an_exception(self) -> None:
        assert issubclass(SEStorageError, Exception)

    @pytest.mark.parametrize("error", [SEStorageError, *SUBCLASSES])
    def test_every_storage_error_is_listed_in_all(self, error: type[SEStorageError]) -> None:
        assert error.__name__ in exceptions.__all__

    def test_all_is_sorted(self) -> None:
        assert exceptions.__all__ == sorted(exceptions.__all__)
