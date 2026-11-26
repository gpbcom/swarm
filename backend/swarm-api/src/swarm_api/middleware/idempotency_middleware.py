from __future__ import annotations

# Standard library imports
from asyncio import CancelledError
from functools import partial
from logging import Logger, getLogger
from typing import ClassVar, List, Optional

# Third-party imports
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# First-party imports
from swarm_api.handlers.problem_handlers import ProblemHandlers
from swarm_models.rest.idempotency.stored_response import StoredResponse
from swarm_service.shared.idempotency.idempotency_service import IdempotencyService
from swarm_web.models.rest.exceptions import SEIdempotencyKeyMissingError, SERestError


class IdempotencyMiddleware:
    """Makes every ``POST`` idempotent: it replays the answer kept under an ``Idempotency-Key``.

    Attributes:
        IDEMPOTENCY_KEY_HEADER (ClassVar[str]): The name of the header that carries the key.
        HEADER_NAME (ClassVar[bytes]): The same name as ASGI gives it, lower case bytes.
        POST_METHOD (ClassVar[str]): The only method the middleware handles.
        HTTP_SCOPE (ClassVar[str]): The scope type of an HTTP request.
        REQUEST_MESSAGE (ClassVar[str]): The type of a message that carries a body chunk.
        START_MESSAGE (ClassVar[str]): The type of the message that starts a response.
        BODY_MESSAGE (ClassVar[str]): The type of a message that carries a response body chunk.
        TYPE_KEY (ClassVar[str]): The ``type`` key of a scope or a message.
        METHOD_KEY (ClassVar[str]): The ``method`` key of a scope.
        PATH_KEY (ClassVar[str]): The ``path`` key of a scope.
        HEADERS_KEY (ClassVar[str]): The ``headers`` key of a scope or a message.
        BODY_KEY (ClassVar[str]): The ``body`` key of a message.
        MORE_BODY_KEY (ClassVar[str]): The ``more_body`` key of a message.
        STATUS_KEY (ClassVar[str]): The ``status`` key of a message.
        ENCODING (ClassVar[str]): The encoding of header names and values.
        app (ASGIApp): The application the middleware wraps.
        service (IdempotencyService): The rules of the key, which keeps the answers.
        logger (Logger): Logger instance.

    Notes:
        - It is written as pure ASGI, not ``BaseHTTPMiddleware``, which cannot hand a buffered body back downstream
          and cancels the route when the client leaves.
        - **The body is buffered whole**, to fingerprint it, then handed downstream unchanged.
        - A request that raises releases its key through ``abandon``, so that a retry runs again.
    """

    IDEMPOTENCY_KEY_HEADER: ClassVar[str] = "Idempotency-Key"
    HEADER_NAME: ClassVar[bytes] = b"idempotency-key"
    POST_METHOD: ClassVar[str] = "POST"
    HTTP_SCOPE: ClassVar[str] = "http"
    REQUEST_MESSAGE: ClassVar[str] = "http.request"
    START_MESSAGE: ClassVar[str] = "http.response.start"
    BODY_MESSAGE: ClassVar[str] = "http.response.body"
    TYPE_KEY: ClassVar[str] = "type"
    METHOD_KEY: ClassVar[str] = "method"
    PATH_KEY: ClassVar[str] = "path"
    HEADERS_KEY: ClassVar[str] = "headers"
    BODY_KEY: ClassVar[str] = "body"
    MORE_BODY_KEY: ClassVar[str] = "more_body"
    STATUS_KEY: ClassVar[str] = "status"
    ENCODING: ClassVar[str] = "latin-1"

    def __init__(self, app: ASGIApp, service: IdempotencyService, logger: Optional[Logger] = None) -> None:
        """Initialise the middleware.

        Args:
            app (ASGIApp): The application to wrap.
            service (IdempotencyService): The rules of the key, which keeps the answers.
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.app = app
        self.service = service
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _key_of(self, scope: Scope) -> Optional[str]:
        """Find the ``Idempotency-Key`` header of a request.

        Args:
            scope (Scope): The ASGI scope.

        Returns:
            Optional[str]: The value of the header, or ``None`` when it is absent.
        """
        for name, value in scope[self.HEADERS_KEY]:
            if name.lower() == self.HEADER_NAME:
                return value.decode(self.ENCODING)
        self.logger.debug("The request has no Idempotency-Key header.")
        return None

    def _stored_response(self, fingerprint: str, messages: List[Message]) -> Optional[StoredResponse]:
        """Build the answer to keep from the messages sent.

        Args:
            fingerprint (str): The fingerprint of the request.
            messages (List[Message]): The messages the application sent.

        Returns:
            Optional[StoredResponse]: The answer, or ``None`` when the application sent no response.
        """
        starts = [message for message in messages if message[self.TYPE_KEY] == self.START_MESSAGE]
        if not starts:
            self.logger.debug("The application sent no response.")
            return None
        headers = [
            (name.decode(self.ENCODING), value.decode(self.ENCODING)) for name, value in starts[0][self.HEADERS_KEY]
        ]
        body = b"".join(
            message.get(self.BODY_KEY, b"") for message in messages if message[self.TYPE_KEY] == self.BODY_MESSAGE
        )
        return StoredResponse(fingerprint=fingerprint, status=starts[0][self.STATUS_KEY], headers=headers, body=body)

    async def _read_body(self, receive: Receive) -> Optional[bytes]:
        """Read the whole body of a request.

        Args:
            receive (Receive): The ASGI receive channel.

        Returns:
            Optional[bytes]: The body, or ``None`` when the client left before the end.
        """
        chunks: List[bytes] = []
        while True:
            message = await receive()
            if message[self.TYPE_KEY] == self.REQUEST_MESSAGE:
                chunks.append(message.get(self.BODY_KEY, b""))
                if not message.get(self.MORE_BODY_KEY, False):
                    self.logger.debug("Buffered a body of %d chunks.", len(chunks))
                    return b"".join(chunks)
            else:
                self.logger.debug("The client left before the end of the body.")
                return None

    async def _replay_body(self, chunks: List[bytes], receive: Receive) -> Message:
        """Give the buffered body to the application, then whatever the client sends next.

        Args:
            chunks (List[bytes]): The buffered body, which holds one item until it is read.
            receive (Receive): The original ASGI receive channel.

        Returns:
            Message: The body message, then the messages of the original channel.
        """
        if chunks:
            body = chunks.pop()
            self.logger.debug("Handing the buffered body downstream.")
            return {self.TYPE_KEY: self.REQUEST_MESSAGE, self.BODY_KEY: body, self.MORE_BODY_KEY: False}
        self.logger.debug("The buffered body was read, waiting for the client.")
        return await receive()

    async def _capture(self, send: Send, messages: List[Message], message: Message) -> None:
        """Keep a copy of a response message and pass it on.

        Args:
            send (Send): The original ASGI send channel.
            messages (List[Message]): Where the messages are kept.
            message (Message): The message to pass on.
        """
        messages.append(message)
        await send(message)

    async def _replay(self, stored: StoredResponse, send: Send) -> None:
        """Send a stored answer again.

        Args:
            stored (StoredResponse): The answer to replay.
            send (Send): The ASGI send channel.
        """
        headers = [(name.encode(self.ENCODING), value.encode(self.ENCODING)) for name, value in stored.headers]
        await send({self.TYPE_KEY: self.START_MESSAGE, self.STATUS_KEY: stored.status, self.HEADERS_KEY: headers})
        await send({self.TYPE_KEY: self.BODY_MESSAGE, self.BODY_KEY: stored.body})
        self.logger.info("Replayed the stored answer with status %d.", stored.status)

    async def _forward(
        self, scope: Scope, receive: Receive, send: Send, key: str, fingerprint: str, body: bytes
    ) -> None:
        """Run the application for a new key, and keep its answer.

        Args:
            scope (Scope): The ASGI scope.
            receive (Receive): The original ASGI receive channel.
            send (Send): The original ASGI send channel.
            key (str): The idempotency key, reserved for this request.
            fingerprint (str): The fingerprint of the request.
            body (bytes): The buffered body.

        Raises:
            Exception: Whatever the application raises, after the key is released.
            CancelledError: If the request is cancelled, after the key is released.
        """
        messages: List[Message] = []
        try:
            await self.app(scope, partial(self._replay_body, [body], receive), partial(self._capture, send, messages))
        except (Exception, CancelledError) as error:
            self.logger.error("The request failed, releasing its key: %s.", type(error).__name__)
            await self.service.abandon(key)
            raise
        stored = self._stored_response(fingerprint, messages)
        if stored is None:
            self.logger.debug("Nothing to keep, releasing the key.")
            await self.service.abandon(key)
        else:
            await self.service.complete(key, stored)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Handle one ASGI call.

        Args:
            scope (Scope): The ASGI scope.
            receive (Receive): The ASGI receive channel.
            send (Send): The ASGI send channel.

        Raises:
            SEIdempotencyKeyMissingError: If the service accepts a request without a key, which it never does.
        """
        if scope[self.TYPE_KEY] != self.HTTP_SCOPE or scope[self.METHOD_KEY] != self.POST_METHOD:
            self.logger.debug("Not a POST, passing through.")
            await self.app(scope, receive, send)
            return
        body = await self._read_body(receive)
        if body is None:
            self.logger.debug("Nothing to answer.")
            return
        path = scope[self.PATH_KEY]
        key = self._key_of(scope)
        fingerprint = self.service.fingerprint(scope[self.METHOD_KEY], path, body)
        try:
            stored = await self.service.begin(key, fingerprint)
        except SERestError as error:
            self.logger.debug("The key is refused with status %d.", error.STATUS)
            response = ProblemHandlers.problem_response(error.STATUS, error.TITLE, str(error) or None, path)
            await response(scope, receive, send)
            return
        if stored is not None:
            self.logger.debug("Replaying.")
            await self._replay(stored, send)
        elif key is not None:
            self.logger.debug("Running the route under a new key.")
            await self._forward(scope, receive, send, key, fingerprint, body)
        else:
            self.logger.error("The service accepted a request without a key.")
            raise SEIdempotencyKeyMissingError("The Idempotency-Key header is required.")
