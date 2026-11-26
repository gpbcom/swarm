from __future__ import annotations

# Standard library imports
import re
from datetime import UTC, datetime, timedelta
from logging import Logger, getLogger
from typing import ClassVar, Dict, Optional, Type

# Third-party imports
from nats.aio.client import Client
from nats.errors import Error as NatsError
from nats.errors import NoRespondersError
from nats.errors import TimeoutError as NatsTimeoutError
from pydantic import BaseModel, ValidationError

# First-party imports
from swarm_nats.models.bus.exceptions import (
    SENatsInvalidDeadlineError,
    SENatsInvalidIdempotencyKeyError,
    SENatsNoResponderError,
    SENatsReplyInvalidError,
    SENatsRequestDeadlineExceededError,
    SENatsRequestFailedError,
)
from swarm_nats.models.bus.nats_headers import NatsHeaders
from swarm_nats.models.config.nats_client_config import NatsClientConfig


class NatsRequester:
    """Sends one request over NATS and waits for its typed reply.

    Attributes:
        ENCODING (ClassVar[str]): The encoding of the body.
        TIMESPEC (ClassVar[str]): The precision of the deadline header, so that it carries microseconds.
        IDEMPOTENCY_KEY_KEY (ClassVar[str]): The header carrying the idempotency key.
        DEADLINE_KEY (ClassVar[str]): The header carrying the absolute deadline.
        connection (Client): The connected NATS client.
        config (NatsClientConfig): The settings, whose ``request_deadline_s`` is the default deadline.
        logger (Logger): Logger instance.

    Notes:
        - **The deadline is absolute, in UTC**, so the responder, and any service it calls in turn, compares it with
          its own clock and stops working on a request nobody waits for any more, whatever the hops in between.
        - **It never retries.** The caller owns the retry and reuses the same idempotency key, so one layer owns each
          retry and the responder can recognise a repeat.
        - A payload and the secret part of a key are never logged.
    """

    ENCODING: ClassVar[str] = "utf-8"
    TIMESPEC: ClassVar[str] = "microseconds"
    IDEMPOTENCY_KEY_KEY: ClassVar[str] = NatsHeaders.IDEMPOTENCY_KEY
    DEADLINE_KEY: ClassVar[str] = NatsHeaders.DEADLINE

    def __init__(self, connection: Client, config: NatsClientConfig, logger: Optional[Logger] = None) -> None:
        """Keep the connection and the settings.

        Args:
            connection (Client): The connected NATS client.
            config (NatsClientConfig): The settings.
            logger (Optional[Logger]): Logger instance.
        """
        self.connection = connection
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _validate(self, idempotency_key: str, deadline_s: float) -> None:
        """Refuse a bad key or a bad deadline before anything is sent.

        Args:
            idempotency_key (str): The key.
            deadline_s (float): The deadline, in seconds.

        Raises:
            SENatsInvalidIdempotencyKeyError: When the key does not match the pattern.
            SENatsInvalidDeadlineError: When the deadline is not positive.
        """
        if not re.match(NatsHeaders.IDEMPOTENCY_KEY_PATTERN, idempotency_key):
            self.logger.error("Refused a request: the idempotency key is malformed.")
            raise SENatsInvalidIdempotencyKeyError(
                f"Invalid idempotency key: {idempotency_key!r}. Must match {NatsHeaders.IDEMPOTENCY_KEY_PATTERN}."
            )
        if deadline_s <= 0:
            self.logger.error("Refused a request: the deadline %s is not positive.", deadline_s)
            raise SENatsInvalidDeadlineError(f"Invalid deadline: {deadline_s!r}. Must be a positive number of seconds.")
        self.logger.debug("The key and the deadline are valid.")

    ############################
    # Publicly Exposed Methods #
    ############################

    async def request[ReplyT: BaseModel](
        self,
        subject: str,
        payload: BaseModel,
        reply_type: Type[ReplyT],
        idempotency_key: str,
        deadline_s: Optional[float] = None,
    ) -> ReplyT:
        """Send one request and decode its reply.

        Args:
            subject (str): The subject to request.
            payload (BaseModel): The body of the request.
            reply_type (Type[ReplyT]): The model of the reply.
            idempotency_key (str): The key that lets the responder recognise a repeat.
            deadline_s (Optional[float]): How long to wait, in seconds, or ``None`` for the configured deadline.

        Returns:
            ReplyT: The decoded reply.

        Raises:
            SENatsInvalidIdempotencyKeyError: When the key is malformed.
            SENatsInvalidDeadlineError: When the deadline is not positive.
            SENatsRequestDeadlineExceededError: When no reply comes in time.
            SENatsNoResponderError: When nobody listens to the subject.
            SENatsRequestFailedError: When the responder reports an error or the request fails.
            SENatsReplyInvalidError: When the reply is not a ``reply_type``.
        """
        if deadline_s is None:
            self.logger.debug("No deadline given, using the configured one.")
            deadline_s = self.config.request_deadline_s
        self._validate(idempotency_key, deadline_s)
        deadline = (datetime.now(UTC) + timedelta(seconds=deadline_s)).isoformat(timespec=self.TIMESPEC)
        headers: Dict[str, str] = {self.IDEMPOTENCY_KEY_KEY: idempotency_key, self.DEADLINE_KEY: deadline}
        self.logger.debug("Requesting %s with a deadline of %s.", subject, deadline)
        try:
            message = await self.connection.request(
                subject, payload.model_dump_json().encode(self.ENCODING), timeout=deadline_s, headers=headers
            )
        except NoRespondersError as error:
            self.logger.error("Nobody answers %s.", subject)
            raise SENatsNoResponderError(f"Invalid subject: {subject!r}. Nobody answers it.") from error
        except NatsTimeoutError as error:
            self.logger.error("The request to %s exceeded its deadline of %s s.", subject, deadline_s)
            raise SENatsRequestDeadlineExceededError(
                f"The request to {subject!r} had no reply within {deadline_s} s."
            ) from error
        except NatsError as error:
            self.logger.error("The request to %s failed: %s.", subject, type(error).__name__)
            raise SENatsRequestFailedError(f"The request to {subject!r} failed with {type(error).__name__}.") from error
        if message.headers and NatsHeaders.ERROR in message.headers:
            error_class = message.headers[NatsHeaders.ERROR]
            self.logger.error("The responder of %s failed with %s.", subject, error_class)
            raise SENatsRequestFailedError(f"The responder of {subject!r} failed with {error_class}.")
        try:
            reply = reply_type.model_validate_json(message.data.decode(self.ENCODING))
        except (ValidationError, UnicodeDecodeError) as error:
            self.logger.error("The reply of %s is not a %s.", subject, reply_type.__name__)
            raise SENatsReplyInvalidError(
                f"Invalid reply: from {subject!r}. Must be a {reply_type.__name__}."
            ) from error
        self.logger.info("Received the reply of %s.", subject)
        return reply
