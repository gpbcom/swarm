from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List, Tuple

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_rest.models.idempotency.exceptions import (
    SEInvalidStoredResponseException,
    SEStoredResponseInvalidBody,
    SEStoredResponseInvalidFingerprint,
    SEStoredResponseInvalidHeaders,
    SEStoredResponseInvalidStatus,
)
from swarm_rest.models.idempotency.stored_response import StoredResponse


class TestStoredResponse:
    FINGERPRINT: ClassVar[str] = "0123456789abcdef" * 4
    HEADERS: ClassVar[List[Tuple[str, str]]] = [("content-type", "application/json"), ("etag", '"v1"')]
    BODY: ClassVar[bytes] = b'{"id": 1}'
    STATUS: ClassVar[int] = 201

    def build(self, **changes: JsonValue) -> StoredResponse:
        values: Dict[str, JsonValue] = {"fingerprint": self.FINGERPRINT, "status": self.STATUS}
        values.update(changes)
        return StoredResponse.model_validate(values)

    def full(self) -> StoredResponse:
        return StoredResponse(fingerprint=self.FINGERPRINT, status=self.STATUS, headers=self.HEADERS, body=self.BODY)

    def test_defaults(self) -> None:
        response = StoredResponse(fingerprint=self.FINGERPRINT, status=200)
        assert response.headers == []
        assert response.body == b""

    def test_full_valid_construction(self) -> None:
        response = self.full()
        assert response.fingerprint == self.FINGERPRINT
        assert response.status == self.STATUS
        assert response.headers == self.HEADERS
        assert response.body == self.BODY

    @pytest.mark.parametrize(("name", "default"), [("headers", []), ("body", b"")])
    def test_none_becomes_the_default(self, name: str, default: JsonValue) -> None:
        assert getattr(self.build(**{name: None}), name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("fingerprint", None, SEStoredResponseInvalidFingerprint),
            ("fingerprint", "", SEStoredResponseInvalidFingerprint),
            ("fingerprint", "abc", SEStoredResponseInvalidFingerprint),
            ("fingerprint", "0123456789ABCDEF" * 4, SEStoredResponseInvalidFingerprint),
            ("fingerprint", "g" * 64, SEStoredResponseInvalidFingerprint),
            ("fingerprint", "a" * 65, SEStoredResponseInvalidFingerprint),
            ("fingerprint", 3, SEStoredResponseInvalidFingerprint),
            ("status", None, SEStoredResponseInvalidStatus),
            ("status", 99, SEStoredResponseInvalidStatus),
            ("status", 600, SEStoredResponseInvalidStatus),
            ("status", True, SEStoredResponseInvalidStatus),
            ("status", 200.5, SEStoredResponseInvalidStatus),
            ("status", "200", SEStoredResponseInvalidStatus),
            ("headers", "content-type", SEStoredResponseInvalidHeaders),
            ("headers", 3, SEStoredResponseInvalidHeaders),
            ("headers", [3], SEStoredResponseInvalidHeaders),
            ("headers", [["", "v"]], SEStoredResponseInvalidHeaders),
            ("headers", [["a"]], SEStoredResponseInvalidHeaders),
            ("headers", [["a", "b", "c"]], SEStoredResponseInvalidHeaders),
            ("headers", [["a", 3]], SEStoredResponseInvalidHeaders),
            ("body", "text", SEStoredResponseInvalidBody),
            ("body", 3, SEStoredResponseInvalidBody),
            ("body", [1, 2], SEStoredResponseInvalidBody),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize(
        "error",
        [
            SEStoredResponseInvalidFingerprint,
            SEStoredResponseInvalidStatus,
            SEStoredResponseInvalidHeaders,
            SEStoredResponseInvalidBody,
        ],
    )
    def test_every_field_error_is_a_stored_response_exception(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidStoredResponseException)

    def test_the_bounds_of_status(self) -> None:
        assert StoredResponse.STATUS_MIN == 100
        assert StoredResponse.STATUS_MAX == 599

    @pytest.mark.parametrize("bound", [StoredResponse.STATUS_MIN, StoredResponse.STATUS_MAX])
    def test_the_bounds_of_status_are_accepted(self, bound: int) -> None:
        assert self.build(status=bound).status == bound

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_assigning_a_field_of_a_built_response_is_refused(self) -> None:
        response = self.full()
        with pytest.raises(ValidationError):
            response.status = 200

    def test_round_trip(self) -> None:
        response = self.full()
        assert StoredResponse.model_validate(response.model_dump()) == response
