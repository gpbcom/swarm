from __future__ import annotations

# Standard library imports
import asyncio
from datetime import UTC, datetime, timedelta
from typing import ClassVar, Dict, List, Optional

# Third-party imports
import pytest
from nats.aio.client import Client
from nats.aio.msg import Msg

# First-party imports
from swarm_nats.clients.nats_requester import NatsRequester
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
from swarm_nats.models.streams.stream_source import StreamSource


class TestNatsRequester:
    SUBJECT = "svc.command"
    KEY = "key-1"
    ENCODING = "utf-8"
    DEADLINE_S = 0.2
    CONFIG_DEADLINE_S = 3.0
    MAX_WAIT_S = 2.0
    TOLERANCE_S = 1.0
    SETTLE_S = 0.2
    PAYLOAD = StreamSource(name="REQUEST", filter_subject="op.a.>")
    REPLY = StreamSource(name="REPLY", domain="edge")
    ERROR_HEADERS: ClassVar[Dict[str, str]] = {NatsHeaders.ERROR: "the responder failed"}
    NOT_A_REPLY = b"not json"

    def setup_method(self) -> None:
        self.received: List[Msg] = []

    async def record_and_reply(self, message: Msg) -> None:
        self.received.append(message)
        await message.respond(self.REPLY.model_dump_json().encode(self.ENCODING))

    async def record_only(self, message: Msg) -> None:
        self.received.append(message)

    async def reply_with_error(self, message: Msg) -> None:
        self.received.append(message)
        message.headers = dict(self.ERROR_HEADERS)
        await message.respond(b"")

    async def reply_with_garbage(self, message: Msg) -> None:
        self.received.append(message)
        await message.respond(self.NOT_A_REPLY)

    def requester(self, client: Client, config: Optional[NatsClientConfig] = None) -> NatsRequester:
        return NatsRequester(client, config if config else NatsClientConfig())

    def deadline_of(self, message: Msg) -> datetime:
        assert message.headers is not None
        return datetime.fromisoformat(message.headers[NatsHeaders.DEADLINE])

    async def test_the_responder_receives_the_body_and_the_two_headers(self, nats_client: Client) -> None:
        await nats_client.subscribe(self.SUBJECT, cb=self.record_and_reply)
        before = datetime.now(UTC)
        await self.requester(nats_client).request(
            self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY, deadline_s=self.CONFIG_DEADLINE_S
        )
        message = self.received[0]
        assert message.data.decode(self.ENCODING) == self.PAYLOAD.model_dump_json()
        assert message.headers is not None
        assert message.headers[NatsHeaders.IDEMPOTENCY_KEY] == self.KEY
        expected = before + timedelta(seconds=self.CONFIG_DEADLINE_S)
        assert abs((self.deadline_of(message) - expected).total_seconds()) < self.TOLERANCE_S

    async def test_the_reply_is_decoded_into_the_reply_type(self, nats_client: Client) -> None:
        await nats_client.subscribe(self.SUBJECT, cb=self.record_and_reply)
        reply = await self.requester(nats_client).request(self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY)
        assert reply == self.REPLY

    async def test_without_a_deadline_the_configured_one_is_used(self, nats_client: Client) -> None:
        config = NatsClientConfig(request_deadline_s=self.CONFIG_DEADLINE_S)
        await nats_client.subscribe(self.SUBJECT, cb=self.record_and_reply)
        before = datetime.now(UTC)
        await self.requester(nats_client, config).request(
            self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY, deadline_s=None
        )
        expected = before + timedelta(seconds=self.CONFIG_DEADLINE_S)
        assert abs((self.deadline_of(self.received[0]) - expected).total_seconds()) < self.TOLERANCE_S

    async def test_a_responder_that_never_answers_exceeds_the_deadline(self, nats_client: Client) -> None:
        await nats_client.subscribe(self.SUBJECT, cb=self.record_only)
        started = asyncio.get_running_loop().time()
        with pytest.raises(SENatsRequestDeadlineExceededError):
            await self.requester(nats_client).request(
                self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY, deadline_s=self.DEADLINE_S
            )
        elapsed = asyncio.get_running_loop().time() - started
        assert self.DEADLINE_S * 0.5 <= elapsed < self.MAX_WAIT_S

    async def test_no_subscriber_raises_no_responder(self, nats_client: Client) -> None:
        with pytest.raises(SENatsNoResponderError):
            await self.requester(nats_client).request(self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY)

    async def test_a_reply_with_the_error_header_is_a_failed_request(self, nats_client: Client) -> None:
        await nats_client.subscribe(self.SUBJECT, cb=self.reply_with_error)
        with pytest.raises(SENatsRequestFailedError):
            await self.requester(nats_client).request(self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY)

    async def test_a_reply_that_does_not_decode_is_invalid(self, nats_client: Client) -> None:
        await nats_client.subscribe(self.SUBJECT, cb=self.reply_with_garbage)
        with pytest.raises(SENatsReplyInvalidError):
            await self.requester(nats_client).request(self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY)

    @pytest.mark.parametrize("key", ["", "a b", "a.b"])
    async def test_a_bad_idempotency_key_is_refused_and_sends_nothing(self, nats_client: Client, key: str) -> None:
        await nats_client.subscribe(self.SUBJECT, cb=self.record_and_reply)
        with pytest.raises(SENatsInvalidIdempotencyKeyError):
            await self.requester(nats_client).request(self.SUBJECT, self.PAYLOAD, StreamSource, key)
        await asyncio.sleep(self.SETTLE_S)
        assert self.received == []

    @pytest.mark.parametrize("deadline_s", [0, -1])
    async def test_a_deadline_that_is_not_positive_is_refused(self, nats_client: Client, deadline_s: float) -> None:
        with pytest.raises(SENatsInvalidDeadlineError):
            await self.requester(nats_client).request(
                self.SUBJECT, self.PAYLOAD, StreamSource, self.KEY, deadline_s=deadline_s
            )
