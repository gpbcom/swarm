from __future__ import annotations

# Standard library imports
import hashlib
import re
from logging import Logger, getLogger
from typing import ClassVar, Optional, Pattern

# First-party imports
from swarm_rest.models.idempotency.stored_response import StoredResponse
from swarm_rest.models.rest.exceptions import (
    SEIdempotencyKeyInFlightError,
    SEIdempotencyKeyInvalidError,
    SEIdempotencyKeyMissingError,
    SEIdempotencyKeyReusedError,
)
from swarm_rest.storage.idempotency.memory_idempotency_store import MemoryIdempotencyStore


class IdempotencyService:
    """The rules of the ``Idempotency-Key`` header: validate a key, replay an answer, refuse a reuse.

    Attributes:
        KEY_LENGTH_MAX (ClassVar[int]): The longest key, in characters.
        KEY_PATTERN (ClassVar[Pattern[str]]): The shape of a key, visible ASCII characters without a space.
        FINGERPRINT_SEPARATOR (ClassVar[bytes]): Separates the parts of a request in its fingerprint.
        ENCODING (ClassVar[str]): The encoding of the method and of the path.
        SERVER_ERROR_MIN (ClassVar[int]): The lowest status that is released instead of stored.
        store (MemoryIdempotencyStore): Where answers and reservations are kept.
        logger (Logger): Logger instance.

    Notes:
        - The methods are coroutines so that a shared store can replace the in-memory one without changing callers.
        - **A key is never logged at INFO or above**, because it may identify a client.
        - A server error is not stored, so that a retry runs the request again.
    """

    KEY_LENGTH_MAX: ClassVar[int] = 255
    KEY_PATTERN: ClassVar[Pattern[str]] = re.compile(r"[\x21-\x7e]+")
    FINGERPRINT_SEPARATOR: ClassVar[bytes] = b"\n"
    ENCODING: ClassVar[str] = "utf-8"
    SERVER_ERROR_MIN: ClassVar[int] = 500

    def __init__(self, store: MemoryIdempotencyStore, logger: Optional[Logger] = None) -> None:
        """Initialise the service.

        Args:
            store (MemoryIdempotencyStore): Where answers and reservations are kept.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.store = store
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Publicly Exposed Methods #
    ############################

    @classmethod
    def fingerprint(cls, method: str, path: str, body: bytes) -> str:
        """Compute the fingerprint of a request.

        Args:
            method (str): The HTTP method.
            path (str): The path of the request.
            body (bytes): The body of the request.

        Returns:
            str: The SHA-256 digest of the method, the path and the body, in lower-case hexadecimal.
        """
        digest = hashlib.sha256()
        digest.update(method.encode(cls.ENCODING))
        digest.update(cls.FINGERPRINT_SEPARATOR)
        digest.update(path.encode(cls.ENCODING))
        digest.update(cls.FINGERPRINT_SEPARATOR)
        digest.update(body)
        return digest.hexdigest()

    async def begin(self, key: Optional[str], fingerprint: str) -> Optional[StoredResponse]:
        """Start a request under its key.

        Args:
            key (Optional[str]): The value of the ``Idempotency-Key`` header.
            fingerprint (str): The fingerprint of the request.

        Returns:
            Optional[StoredResponse]: The answer to replay, or ``None`` when the key is now reserved for this request.

        Raises:
            SEIdempotencyKeyMissingError: If the key is missing.
            SEIdempotencyKeyInvalidError: If the key is empty, too long or has characters outside visible ASCII.
            SEIdempotencyKeyReusedError: If the key was used for another request.
            SEIdempotencyKeyInFlightError: If a request with the key is still running.
        """
        if key is None:
            self.logger.error("The Idempotency-Key is missing.")
            raise SEIdempotencyKeyMissingError("The Idempotency-Key header is required.")
        if len(key) > self.KEY_LENGTH_MAX or not self.KEY_PATTERN.fullmatch(key):
            self.logger.error("The Idempotency-Key has an invalid shape.")
            raise SEIdempotencyKeyInvalidError(
                f"Invalid Idempotency-Key. Must be 1 to {self.KEY_LENGTH_MAX} visible ASCII characters."
            )
        stored = self.store.get(key)
        if stored is not None:
            if stored.fingerprint != fingerprint:
                self.logger.error("The Idempotency-Key was used for another request.")
                raise SEIdempotencyKeyReusedError("The Idempotency-Key was used for another request.")
            self.logger.debug("Replaying the stored answer.")
            return stored
        if not self.store.reserve(key):
            self.logger.error("A request with the Idempotency-Key is still running.")
            raise SEIdempotencyKeyInFlightError("A request with the Idempotency-Key is still running.")
        self.logger.debug("The key is new and reserved.")
        return None

    async def complete(self, key: str, response: StoredResponse) -> None:
        """End a request: keep its answer, or release the key after a server error.

        Args:
            key (str): The idempotency key.
            response (StoredResponse): The answer given to the client.
        """
        if response.status >= self.SERVER_ERROR_MIN:
            self.store.release(key)
            self.logger.debug("A server error is not stored, the key is released.")
        else:
            self.store.save(key, response)
            self.logger.debug("The answer is stored.")

    async def abandon(self, key: str) -> None:
        """Give up a request that did not answer, and release its key.

        Args:
            key (str): The idempotency key.
        """
        self.store.release(key)
        self.logger.debug("The request was abandoned, the key is released.")
