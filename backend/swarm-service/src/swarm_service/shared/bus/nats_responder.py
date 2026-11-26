from __future__ import annotations

# Standard library imports
import asyncio
import re
from datetime import UTC, datetime
from logging import Logger, getLogger
from typing import Awaitable, Callable, ClassVar, Dict, Optional, Pattern, Type

# Third-party imports
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.aio.subscription import Subscription
from nats.errors import Error as NatsError
from nats.js.api import KeyValueConfig
from nats.js.errors import BadRequestError, KeyNotFoundError
from nats.js.kv import KeyValue
from pydantic import BaseModel, ValidationError

# First-party imports
from swarm_lifecycle.runnables.async_runnable import AsyncRunnable
from swarm_nats.models.bus.exceptions import (
    SENatsInvalidDeadlineError,
    SENatsInvalidIdempotencyKeyError,
    SENatsRequestInvalidError,
)
from swarm_nats.models.bus.nats_headers import NatsHeaders
from swarm_nats.models.config.nats_responder_config import NatsResponderConfig


class NatsResponder[Q: BaseModel, R: BaseModel](AsyncRunnable):
    """Answer the requests of one subject, once per idempotency key, within their deadline.

    Attributes:
        connection (Client): The connected NATS client.
        config (NatsResponderConfig): The subject, queue group, bucket and status interval.
        request_type (Type[Q]): The model every request body must validate against.
        handler (Callable[[Q], Awaitable[R]]): The business call that turns a request into a reply.
        bucket (Optional[KeyValue]): The key-value bucket that stores the replies, once ``initialize`` has run.
        subscription (Optional[Subscription]): The subscription to the subject, once ``initialize`` has run.
        stopped (asyncio.Event): Set by ``close`` to end ``run``.
        HISTORY (int): The history of the bucket, only the last reply of a key is useful.
        KEY_PATTERN (Pattern[str]): The shape of an idempotency key.
        logger (Logger): Logger instance.

    Notes:
        - Every request carries an idempotency key and an absolute deadline in its headers.
        - A request whose deadline is past is dropped without a reply, because its caller has stopped waiting.
        - **A failed request is never stored**, so that a retry with the same key calls the handler again: only a
          reply that succeeded must be replayed.
        - The error name of a reply is the class name of the error, so that the caller can map it back.
        - One layer owns each retry: this class never retries, the caller does.
    """

    HISTORY: ClassVar[int] = 1
    KEY_PATTERN: ClassVar[Pattern[str]] = re.compile(NatsHeaders.IDEMPOTENCY_KEY_PATTERN)

    def __init__(
        self,
        connection: Client,
        config: NatsResponderConfig,
        request_type: Type[Q],
        handler: Callable[[Q], Awaitable[R]],
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialise the responder.

        Args:
            connection (Client): The connected NATS client.
            config (NatsResponderConfig): The settings of the responder.
            request_type (Type[Q]): The model of the request body.
            handler (Callable[[Q], Awaitable[R]]): The coroutine that answers one request.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        super().__init__(config.status_interval_s)
        self.logger = logger if logger else getLogger(__name__)
        self.connection = connection
        self.config = config
        self.request_type = request_type
        self.handler = handler
        self.bucket: Optional[KeyValue] = None
        self.subscription: Optional[Subscription] = None
        self.stopped = asyncio.Event()

    ############################
    # Internal Helpers Methods #
    ############################

    async def _open_bucket(self) -> KeyValue:
        """Create the idempotency bucket, or bind it when it already exists with other settings.

        Returns:
            KeyValue: The bucket.
        """
        context = self.connection.jetstream()
        bucket_config = KeyValueConfig(
            bucket=self.config.idempotency_bucket,
            history=self.HISTORY,
            ttl=self.config.idempotency_ttl_s,
            replicas=self.config.replicas,
        )
        try:
            bucket = await context.create_key_value(config=bucket_config)
        except BadRequestError:
            self.logger.debug("Bucket %s exists with other settings, binding it.", self.config.idempotency_bucket)
            return await context.key_value(self.config.idempotency_bucket)
        self.logger.debug("Created or found bucket %s.", self.config.idempotency_bucket)
        return bucket

    async def _reply(self, msg: Msg, data: bytes, error: Optional[str] = None) -> None:
        """Send one reply, with the error name in its headers when there is one.

        Args:
            msg (Msg): The request.
            data (bytes): The body of the reply.
            error (Optional[str]): The class name of the error, or ``None`` for a success.
        """
        if not msg.reply:
            self.logger.debug("Request has no reply subject, nothing to send.")
            return
        headers: Optional[Dict[str, str]] = None
        if error is not None:
            headers = {NatsHeaders.ERROR: error}
        else:
            self.logger.debug("Reply carries no error.")
        await self.connection.publish(msg.reply, data, headers=headers)

    def _read_key(self, headers: Dict[str, str]) -> str:
        """Read the idempotency key of a request.

        Args:
            headers (Dict[str, str]): The headers of the request.

        Returns:
            str: The key.

        Raises:
            SENatsInvalidIdempotencyKeyError: If the key is missing or malformed.
        """
        key = headers.get(NatsHeaders.IDEMPOTENCY_KEY)
        if key is None or not self.KEY_PATTERN.match(key):
            self.logger.error("Refused a request with a missing or invalid idempotency key.")
            raise SENatsInvalidIdempotencyKeyError(
                f"Invalid idempotency key: {key!r}. Must match {NatsHeaders.IDEMPOTENCY_KEY_PATTERN}."
            )
        self.logger.debug("Request has a valid idempotency key.")
        return key

    def _read_deadline(self, headers: Dict[str, str]) -> datetime:
        """Read the absolute deadline of a request.

        Args:
            headers (Dict[str, str]): The headers of the request.

        Returns:
            datetime: The deadline, with its time zone.

        Raises:
            SENatsInvalidDeadlineError: If the deadline is missing, malformed or has no time zone.
        """
        raw = headers.get(NatsHeaders.DEADLINE)
        if raw is None:
            self.logger.error("Refused a request without a deadline.")
            raise SENatsInvalidDeadlineError(f"Invalid deadline: {raw!r}. Must be an ISO 8601 date and time.")
        try:
            deadline = datetime.fromisoformat(raw)
        except ValueError as error:
            self.logger.error("Refused a request with a malformed deadline, %s.", type(error).__name__)
            raise SENatsInvalidDeadlineError(
                f"Invalid deadline: {raw!r}. Must be an ISO 8601 date and time."
            ) from error
        if deadline.tzinfo is None:
            self.logger.error("Refused a request with a deadline that has no time zone.")
            raise SENatsInvalidDeadlineError(f"Invalid deadline: {raw!r}. Must carry a time zone.")
        self.logger.debug("Request has a valid deadline.")
        return deadline

    async def _stored_reply(self, bucket: KeyValue, key: str) -> Optional[bytes]:
        """Read the reply already stored under a key.

        Args:
            bucket (KeyValue): The idempotency bucket.
            key (str): The idempotency key.

        Returns:
            Optional[bytes]: The stored reply, or ``None`` when the key is new.
        """
        try:
            entry = await bucket.get(key)
        except KeyNotFoundError:
            self.logger.debug("Idempotency key is new.")
            return None
        if entry.value is None:
            self.logger.debug("Idempotency key holds no value, treating it as new.")
            return None
        self.logger.debug("Idempotency key already stored.")
        return entry.value

    async def _answer(self, bucket: KeyValue, msg: Msg) -> None:
        """Answer one request, replying with the error name when it cannot be served.

        Args:
            bucket (KeyValue): The idempotency bucket.
            msg (Msg): The request.
        """
        headers: Dict[str, str] = {}
        if msg.headers:
            headers = msg.headers
        else:
            self.logger.debug("Request has no headers.")
        try:
            key = self._read_key(headers)
        except SENatsInvalidIdempotencyKeyError as error:
            await self._reply(msg, b"", type(error).__name__)
            return
        try:
            deadline = self._read_deadline(headers)
        except SENatsInvalidDeadlineError as error:
            await self._reply(msg, b"", type(error).__name__)
            return
        if deadline <= datetime.now(UTC):
            self.logger.warning("Dropped a request whose deadline is past, without a reply.")
            return
        self.logger.debug("Deadline is not past.")
        stored = await self._stored_reply(bucket, key)
        if stored is not None:
            self.logger.debug("Replaying the stored reply without calling the handler.")
            await self._reply(msg, stored)
            return
        try:
            request = self.request_type.model_validate_json(msg.data)
        except ValidationError as error:
            self.logger.error("Refused a request body that is not a valid %s.", self.request_type.__name__)
            await self._reply(msg, str(error).encode(), SENatsRequestInvalidError.__name__)
            return
        try:
            result = await self.handler(request)
        except Exception as error:  # noqa: BLE001
            self.logger.error("Handler failed with %s, the failure is not stored.", type(error).__name__)
            await self._reply(msg, b"", type(error).__name__)
            return
        data = result.model_dump_json().encode()
        await bucket.put(key, data)
        self.logger.debug("Stored the reply under its idempotency key.")
        await self._reply(msg, data)

    async def _on_message(self, msg: Msg) -> None:
        """Handle one message of the subscription.

        Args:
            msg (Msg): The request.
        """
        if self.bucket is None:
            self.logger.error("Received a request before the bucket was ready.")
            return
        self.logger.debug("Received a request on %s.", msg.subject)
        await self._answer(self.bucket, msg)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def initialize(self) -> None:
        """Create or bind the idempotency bucket, then subscribe to the subject in the queue group."""
        self.bucket = await self._open_bucket()
        self.subscription = await self.connection.subscribe(
            self.config.subject, queue=self.config.queue_group, cb=self._on_message
        )
        self.logger.info("Responding on %s in %s.", self.config.subject, self.config.queue_group)

    async def run(self) -> None:
        """Wait until the responder is closed or cancelled."""
        await self.stopped.wait()
        self.logger.debug("Responder stopped.")

    async def close(self) -> None:
        """Unsubscribe. It is safe after a failed or partial ``initialize``."""
        self.stopped.set()
        if self.subscription is None:
            self.logger.debug("No subscription to close.")
            return
        try:
            await self.subscription.unsubscribe()
        except NatsError as error:
            self.logger.warning("Could not unsubscribe, %s.", type(error).__name__)
        else:
            self.logger.info("Stopped responding on %s.", self.config.subject)
        self.subscription = None
