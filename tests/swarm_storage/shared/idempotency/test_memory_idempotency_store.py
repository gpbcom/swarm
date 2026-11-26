from __future__ import annotations

# Standard library imports
from typing import ClassVar

# Third-party imports
from manual_clock import ManualClock

# First-party imports
from swarm_models.rest.idempotency.stored_response import StoredResponse
from swarm_storage.shared.idempotency.memory_idempotency_store import MemoryIdempotencyStore


class TestMemoryIdempotencyStore:
    TTL_S: ClassVar[float] = 60.0
    MAX_ENTRIES: ClassVar[int] = 2
    KEY: ClassVar[str] = "key-1"
    KEY_B: ClassVar[str] = "key-2"
    KEY_C: ClassVar[str] = "key-3"
    FINGERPRINT: ClassVar[str] = "a" * 64
    STATUS_OK: ClassVar[int] = 201

    def a_store(self, clock: ManualClock) -> MemoryIdempotencyStore:
        return MemoryIdempotencyStore(ttl_s=self.TTL_S, max_entries=self.MAX_ENTRIES, clock=clock)

    def a_response(self) -> StoredResponse:
        return StoredResponse(fingerprint=self.FINGERPRINT, status=self.STATUS_OK)

    def test_a_free_key_is_reserved_and_in_flight(self) -> None:
        store = self.a_store(ManualClock())
        assert store.reserve(self.KEY) is True
        assert store.is_in_flight(self.KEY) is True

    def test_a_key_in_flight_cannot_be_reserved_again(self) -> None:
        store = self.a_store(ManualClock())
        store.reserve(self.KEY)
        assert store.reserve(self.KEY) is False

    def test_saving_stores_the_response_and_ends_the_in_flight_state(self) -> None:
        store = self.a_store(ManualClock())
        store.reserve(self.KEY)
        response = self.a_response()
        store.save(self.KEY, response)
        assert store.get(self.KEY) == response
        assert store.is_in_flight(self.KEY) is False
        assert store.size == 1

    def test_a_stored_key_cannot_be_reserved(self) -> None:
        store = self.a_store(ManualClock())
        store.reserve(self.KEY)
        store.save(self.KEY, self.a_response())
        assert store.reserve(self.KEY) is False

    def test_an_unknown_key_has_no_response(self) -> None:
        store = self.a_store(ManualClock())
        assert store.get(self.KEY) is None

    def test_a_stored_response_is_returned_until_the_ttl_has_passed(self) -> None:
        clock = ManualClock()
        store = self.a_store(clock)
        response = self.a_response()
        store.save(self.KEY, response)
        clock.advance(self.TTL_S - 1.0)
        assert store.get(self.KEY) == response
        clock.advance(2.0)
        assert store.get(self.KEY) is None
        assert store.size == 0

    def test_an_expired_key_can_be_reserved_again(self) -> None:
        clock = ManualClock()
        store = self.a_store(clock)
        store.save(self.KEY, self.a_response())
        clock.advance(self.TTL_S + 1.0)
        assert store.reserve(self.KEY) is True

    def test_saving_beyond_max_entries_drops_the_oldest_entry(self) -> None:
        clock = ManualClock()
        store = self.a_store(clock)
        for key in (self.KEY, self.KEY_B, self.KEY_C):
            store.save(key, self.a_response())
            clock.advance(1.0)
        assert store.size == self.MAX_ENTRIES
        assert store.get(self.KEY) is None
        assert store.get(self.KEY_B) is not None
        assert store.get(self.KEY_C) is not None

    def test_release_frees_the_key_for_a_new_reserve(self) -> None:
        store = self.a_store(ManualClock())
        store.reserve(self.KEY)
        store.release(self.KEY)
        assert store.is_in_flight(self.KEY) is False
        assert store.get(self.KEY) is None
        assert store.reserve(self.KEY) is True
