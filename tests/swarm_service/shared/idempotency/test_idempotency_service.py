from __future__ import annotations

# Standard library imports
import hashlib
from typing import ClassVar, List, Optional

# Third-party imports
import pytest

# First-party imports
from swarm_models.rest.idempotency.stored_response import StoredResponse
from swarm_service.shared.idempotency.idempotency_service import IdempotencyService
from swarm_storage.shared.idempotency.memory_idempotency_store import MemoryIdempotencyStore
from swarm_web.models.rest.exceptions import (
    SEIdempotencyKeyInFlightError,
    SEIdempotencyKeyInvalidError,
    SEIdempotencyKeyMissingError,
    SEIdempotencyKeyReusedError,
)


class TestIdempotencyService:
    KEY: ClassVar[str] = "key-1"
    METHOD: ClassVar[str] = "POST"
    PATH: ClassVar[str] = "/missions"
    BODY: ClassVar[bytes] = b"payload"
    STATUS_CREATED: ClassVar[int] = 201
    STATUS_CLIENT_ERROR: ClassVar[int] = 422
    STATUS_SERVER_ERROR: ClassVar[int] = 503
    TTL_S: ClassVar[float] = 60.0
    MAX_ENTRIES: ClassVar[int] = 10
    INVALID_KEYS: ClassVar[List[str]] = ["", "has space", "tab\tkey", "café", "ctrl\x7f", "x" * 256]

    def a_service(self) -> IdempotencyService:
        return IdempotencyService(MemoryIdempotencyStore(ttl_s=self.TTL_S, max_entries=self.MAX_ENTRIES))

    def a_response(self, fingerprint: str, status: int) -> StoredResponse:
        return StoredResponse(fingerprint=fingerprint, status=status)

    def a_fingerprint(self) -> str:
        return IdempotencyService.fingerprint(self.METHOD, self.PATH, self.BODY)

    def test_the_key_length_maximum_is_255(self) -> None:
        assert IdempotencyService.KEY_LENGTH_MAX == 255

    def test_the_fingerprint_is_a_sha256_hex_digest(self) -> None:
        fingerprint = self.a_fingerprint()
        assert len(fingerprint) == len(hashlib.sha256().hexdigest())
        assert fingerprint == fingerprint.lower()
        int(fingerprint, 16)

    def test_equal_requests_have_equal_fingerprints(self) -> None:
        assert self.a_fingerprint() == IdempotencyService.fingerprint(self.METHOD, self.PATH, self.BODY)

    def test_another_body_or_path_has_another_fingerprint(self) -> None:
        assert IdempotencyService.fingerprint(self.METHOD, self.PATH, b"other") != self.a_fingerprint()
        assert IdempotencyService.fingerprint(self.METHOD, "/fleet", self.BODY) != self.a_fingerprint()

    async def test_a_missing_key_is_refused(self) -> None:
        with pytest.raises(SEIdempotencyKeyMissingError):
            await self.a_service().begin(None, self.a_fingerprint())

    @pytest.mark.parametrize("key", INVALID_KEYS)
    async def test_an_invalid_key_is_refused(self, key: str) -> None:
        with pytest.raises(SEIdempotencyKeyInvalidError):
            await self.a_service().begin(key, self.a_fingerprint())

    async def test_a_key_of_the_maximum_length_is_accepted(self) -> None:
        key = "x" * IdempotencyService.KEY_LENGTH_MAX
        assert await self.a_service().begin(key, self.a_fingerprint()) is None

    async def test_a_new_key_is_reserved_and_nothing_is_returned(self) -> None:
        service = self.a_service()
        assert await service.begin(self.KEY, self.a_fingerprint()) is None
        assert service.store.is_in_flight(self.KEY) is True

    async def test_a_key_in_flight_is_refused(self) -> None:
        service = self.a_service()
        await service.begin(self.KEY, self.a_fingerprint())
        with pytest.raises(SEIdempotencyKeyInFlightError):
            await service.begin(self.KEY, self.a_fingerprint())

    async def test_a_stored_response_with_the_same_fingerprint_is_replayed(self) -> None:
        service = self.a_service()
        response = self.a_response(self.a_fingerprint(), self.STATUS_CREATED)
        await service.begin(self.KEY, self.a_fingerprint())
        await service.complete(self.KEY, response)
        replayed: Optional[StoredResponse] = await service.begin(self.KEY, self.a_fingerprint())
        assert replayed == response

    async def test_a_stored_response_with_another_fingerprint_is_refused(self) -> None:
        service = self.a_service()
        await service.begin(self.KEY, self.a_fingerprint())
        await service.complete(self.KEY, self.a_response(self.a_fingerprint(), self.STATUS_CREATED))
        other = IdempotencyService.fingerprint(self.METHOD, self.PATH, b"other")
        with pytest.raises(SEIdempotencyKeyReusedError):
            await service.begin(self.KEY, other)

    async def test_a_client_error_response_is_stored(self) -> None:
        service = self.a_service()
        await service.begin(self.KEY, self.a_fingerprint())
        await service.complete(self.KEY, self.a_response(self.a_fingerprint(), self.STATUS_CLIENT_ERROR))
        assert service.store.get(self.KEY) is not None

    async def test_a_server_error_is_released_and_a_retry_runs_again(self) -> None:
        service = self.a_service()
        await service.begin(self.KEY, self.a_fingerprint())
        await service.complete(self.KEY, self.a_response(self.a_fingerprint(), self.STATUS_SERVER_ERROR))
        assert service.store.get(self.KEY) is None
        assert service.store.is_in_flight(self.KEY) is False
        assert await service.begin(self.KEY, self.a_fingerprint()) is None

    async def test_abandon_releases_the_key(self) -> None:
        service = self.a_service()
        await service.begin(self.KEY, self.a_fingerprint())
        await service.abandon(self.KEY)
        assert service.store.is_in_flight(self.KEY) is False
        assert await service.begin(self.KEY, self.a_fingerprint()) is None
