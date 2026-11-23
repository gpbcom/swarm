from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from time import monotonic
from typing import Callable, Dict, Optional, Set, Tuple

# First-party imports
from swarm_rest.models.idempotency.stored_response import StoredResponse


class MemoryIdempotencyStore:
    """Keeps idempotent answers in the memory of the process.

    Attributes:
        ttl_s (float): How long an answer is kept, in seconds.
        max_entries (int): How many answers are kept at most.
        clock (Callable[[], float]): Gives the current time in seconds.
        entries (Dict[str, Tuple[float, StoredResponse]]): The answers by key, with their expiry time, the oldest first.
        in_flight (Set[str]): The keys whose request is running.
        logger (Logger): Logger instance.

    Notes:
        - **The store is not shared between processes.** Several replicas need a shared store with the same methods.
        - The oldest answer is the one saved first, and it is dropped first when ``max_entries`` is exceeded.
        - Reservations are not counted in ``size`` and never expire: the service releases them.
    """

    def __init__(
        self,
        ttl_s: float,
        max_entries: int,
        clock: Callable[[], float] = monotonic,
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the store.

        Args:
            ttl_s (float): How long an answer is kept, in seconds.
            max_entries (int): How many answers are kept at most.
            clock (Callable[[], float]): Gives the current time in seconds.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.ttl_s = ttl_s
        self.max_entries = max_entries
        self.clock = clock
        self.entries: Dict[str, Tuple[float, StoredResponse]] = {}
        self.in_flight: Set[str] = set()
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    @property
    def size(self) -> int:
        """Return how many answers are stored.

        Returns:
            int: The number of stored answers, expired ones excluded.
        """
        self.purge()
        return len(self.entries)

    def purge(self) -> None:
        """Remove every expired answer."""
        now_s = self.clock()
        expired = [key for key, (expires_s, _) in self.entries.items() if expires_s <= now_s]
        for key in expired:
            del self.entries[key]
        if expired:
            self.logger.debug("Purged %d expired answers.", len(expired))
        else:
            self.logger.debug("No expired answer to purge.")

    def get(self, key: str) -> Optional[StoredResponse]:
        """Return the answer stored for a key.

        Args:
            key (str): The idempotency key.

        Returns:
            Optional[StoredResponse]: The answer, or ``None`` when there is none or it has expired.
        """
        entry = self.entries.get(key)
        if entry is None:
            self.logger.debug("No answer stored for the key.")
            return None
        expires_s, response = entry
        if expires_s <= self.clock():
            del self.entries[key]
            self.logger.debug("The answer of the key has expired and is removed.")
            return None
        self.logger.debug("Found the answer of the key.")
        return response

    def is_in_flight(self, key: str) -> bool:
        """Tell whether the request of a key is running.

        Args:
            key (str): The idempotency key.

        Returns:
            bool: ``True`` when the key is reserved.
        """
        return key in self.in_flight

    def reserve(self, key: str) -> bool:
        """Reserve a key for a request that is about to run.

        Args:
            key (str): The idempotency key.

        Returns:
            bool: ``True`` when the key was free, ``False`` when it is in flight or already has an answer.
        """
        if key in self.in_flight:
            self.logger.debug("The key is already in flight.")
            return False
        if self.get(key) is not None:
            self.logger.debug("The key already has an answer.")
            return False
        self.in_flight.add(key)
        self.logger.debug("Reserved the key.")
        return True

    def release(self, key: str) -> None:
        """Release the reservation of a key, whether or not it exists.

        Args:
            key (str): The idempotency key.
        """
        if key in self.in_flight:
            self.in_flight.discard(key)
            self.logger.debug("Released the key.")
        else:
            self.logger.debug("The key was not in flight, nothing to release.")

    def save(self, key: str, response: StoredResponse) -> None:
        """Store the answer of a key and end its reservation.

        Args:
            key (str): The idempotency key.
            response (StoredResponse): The answer to keep.
        """
        self.in_flight.discard(key)
        self.entries.pop(key, None)
        self.entries[key] = (self.clock() + self.ttl_s, response)
        self.purge()
        while len(self.entries) > self.max_entries:
            oldest = next(iter(self.entries))
            del self.entries[oldest]
            self.logger.debug("Dropped the oldest answer to stay within %d entries.", self.max_entries)
        self.logger.info("Stored an answer, %d kept.", len(self.entries))
