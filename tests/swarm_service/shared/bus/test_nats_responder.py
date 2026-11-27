from __future__ import annotations

# Standard library imports
import asyncio
from datetime import UTC, datetime, timedelta
from typing import AsyncIterator, ClassVar, Dict, List, Optional

# Third-party imports
import pytest
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.errors import TimeoutError as NatsTimeoutError
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import SpanKind, StatusCode

# First-party imports
from swarm_lifecycle.models.enums import RunnableStatus
from swarm_models.config.nats.nats_responder_config import NatsResponderConfig
from swarm_models.streams.stream_source import StreamSource
from swarm_nats.models.bus.nats_headers import NatsHeaders
from swarm_service.shared.bus.nats_responder import NatsResponder
from tests.fakes.signals.recorded_signals import RecordedSignals


class TestNatsResponder:
    SUBJECT: ClassVar[str] = "svc.echo"
    QUEUE_GROUP: ClassVar[str] = "echo_workers"
    BUCKET: ClassVar[str] = "idempotency_test"
    TTL_S: ClassVar[float] = 600.0
    STATUS_INTERVAL_S: ClassVar[float] = 0.05
    TIMEOUT_S: ClassVar[float] = 5.0
    SHORT_TIMEOUT_S: ClassVar[float] = 0.5
    DEADLINE_S: ClassVar[float] = 30.0
    REPLY_SUFFIX: ClassVar[str] = "_reply"
    FAILING_NAME: ClassVar[str] = "failing"
    REQUEST_NAME: ClassVar[str] = "origin"
    KEY: ClassVar[str] = "key-1"
    OTHER_KEY: ClassVar[str] = "key-2"
    BAD_BODY: ClassVar[bytes] = b'{"unexpected": true}'
    INVALID_KEY_ERROR: ClassVar[str] = "SENatsInvalidIdempotencyKeyError"
    INVALID_DEADLINE_ERROR: ClassVar[str] = "SENatsInvalidDeadlineError"
    INVALID_REQUEST_ERROR: ClassVar[str] = "SENatsRequestInvalidError"
    HANDLER_ERROR: ClassVar[str] = "ValueError"
    TRACEPARENT_HEADER: ClassVar[str] = "traceparent"
    TRACE_ID: ClassVar[int] = 0x4BF92F3577B34DA6A3CE929D0E0E4736
    PARENT_SPAN_ID: ClassVar[int] = 0x00F067AA0BA902B7
    TRACEPARENT: ClassVar[str] = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"

    calls: List[StreamSource]
    tasks: List[asyncio.Task[None]]
    statuses: List[RunnableStatus]

    @pytest.fixture(autouse=True)
    async def serving(self) -> AsyncIterator[None]:
        self.calls = []
        self.tasks = []
        self.statuses = []
        yield
        for task in self.tasks:
            task.cancel()
        for task in self.tasks:
            try:
                await task
            except asyncio.CancelledError:
                continue

    @pytest.fixture
    def config(self) -> NatsResponderConfig:
        return NatsResponderConfig(
            subject=self.SUBJECT,
            queue_group=self.QUEUE_GROUP,
            idempotency_bucket=self.BUCKET,
            idempotency_ttl_s=self.TTL_S,
            replicas=1,
            status_interval_s=self.STATUS_INTERVAL_S,
        )

    async def handle(self, request: StreamSource) -> StreamSource:
        self.calls.append(request)
        if request.name == self.FAILING_NAME:
            raise ValueError(request.name)
        return StreamSource(name=request.name + self.REPLY_SUFFIX)

    async def consume(self, responder: NatsResponder[StreamSource, StreamSource]) -> None:
        async for status in responder.execute():
            self.statuses.append(status)

    async def launch(self, client: Client, config: NatsResponderConfig) -> NatsResponder[StreamSource, StreamSource]:
        responder = NatsResponder(client, config, StreamSource, self.handle)
        self.tasks.append(asyncio.create_task(self.consume(responder)))
        async with asyncio.timeout(self.TIMEOUT_S):
            while responder.status != RunnableStatus.RUNNING:
                await asyncio.sleep(self.STATUS_INTERVAL_S / 5)
        return responder

    def headers(self, key: Optional[str], deadline: Optional[str]) -> Dict[str, str]:
        result: Dict[str, str] = {}
        if key is not None:
            result[NatsHeaders.IDEMPOTENCY_KEY] = key
        if deadline is not None:
            result[NatsHeaders.DEADLINE] = deadline
        return result

    def deadline(self, offset_s: float) -> str:
        return (datetime.now(UTC) + timedelta(seconds=offset_s)).isoformat()

    def body(self, name: str) -> bytes:
        return StreamSource(name=name).model_dump_json().encode()

    async def ask(
        self,
        client: Client,
        key: Optional[str],
        deadline: Optional[str],
        data: Optional[bytes] = None,
        timeout_s: Optional[float] = None,
    ) -> Msg:
        return await client.request(
            self.SUBJECT,
            self.body(self.REQUEST_NAME) if data is None else data,
            timeout=self.TIMEOUT_S if timeout_s is None else timeout_s,
            headers=self.headers(key, deadline),
        )

    async def test_a_valid_request_gets_the_handler_reply_as_json(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        reply = await self.ask(nats_client, self.KEY, self.deadline(self.DEADLINE_S))
        assert StreamSource.model_validate_json(reply.data) == StreamSource(name=self.REQUEST_NAME + self.REPLY_SUFFIX)
        assert self.calls == [StreamSource(name=self.REQUEST_NAME)]

    async def test_the_same_idempotency_key_calls_the_handler_once(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        first = await self.ask(nats_client, self.KEY, self.deadline(self.DEADLINE_S))
        second = await self.ask(nats_client, self.KEY, self.deadline(self.DEADLINE_S))
        assert first.data == second.data
        assert len(self.calls) == 1

    async def test_another_idempotency_key_calls_the_handler_again(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        await self.ask(nats_client, self.KEY, self.deadline(self.DEADLINE_S))
        await self.ask(nats_client, self.OTHER_KEY, self.deadline(self.DEADLINE_S))
        assert len(self.calls) == 2

    @pytest.mark.parametrize("key", [None, "a b"])
    async def test_a_missing_or_invalid_idempotency_key_is_refused(
        self, nats_client: Client, config: NatsResponderConfig, key: Optional[str]
    ) -> None:
        await self.launch(nats_client, config)
        reply = await self.ask(nats_client, key, self.deadline(self.DEADLINE_S))
        assert reply.headers[NatsHeaders.ERROR] == self.INVALID_KEY_ERROR
        assert self.calls == []

    @pytest.mark.parametrize("deadline", [None, "tomorrow"])
    async def test_a_missing_or_malformed_deadline_is_refused(
        self, nats_client: Client, config: NatsResponderConfig, deadline: Optional[str]
    ) -> None:
        await self.launch(nats_client, config)
        reply = await self.ask(nats_client, self.KEY, deadline)
        assert reply.headers[NatsHeaders.ERROR] == self.INVALID_DEADLINE_ERROR
        assert self.calls == []

    async def test_a_deadline_already_past_gets_no_reply(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        with pytest.raises(NatsTimeoutError):
            await self.ask(nats_client, self.KEY, self.deadline(-self.DEADLINE_S), timeout_s=self.SHORT_TIMEOUT_S)
        assert self.calls == []

    async def test_a_body_that_is_not_a_valid_request_is_refused(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        reply = await self.ask(nats_client, self.KEY, self.deadline(self.DEADLINE_S), data=self.BAD_BODY)
        assert reply.headers[NatsHeaders.ERROR] == self.INVALID_REQUEST_ERROR
        assert self.calls == []

    async def test_a_handler_error_is_reported_and_not_stored(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        body = self.body(self.FAILING_NAME)
        first = await self.ask(nats_client, self.KEY, self.deadline(self.DEADLINE_S), data=body)
        second = await self.ask(nats_client, self.KEY, self.deadline(self.DEADLINE_S), data=body)
        assert first.headers[NatsHeaders.ERROR] == self.HANDLER_ERROR
        assert second.headers[NatsHeaders.ERROR] == self.HANDLER_ERROR
        assert len(self.calls) == 2

    async def test_the_idempotency_bucket_exists_with_its_ttl(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        bucket = await nats_client.jetstream().key_value(self.BUCKET)
        status = await bucket.status()
        assert status.ttl == self.TTL_S

    async def test_two_responders_in_one_queue_group_handle_each_request_once(
        self, nats_client: Client, config: NatsResponderConfig
    ) -> None:
        await self.launch(nats_client, config)
        await self.launch(nats_client, config)
        keys = [f"{self.KEY}-{index}" for index in range(10)]
        for key in keys:
            await self.ask(nats_client, key, self.deadline(self.DEADLINE_S))
        assert len(self.calls) == len(keys)

    async def test_execute_yields_running_while_serving(self, nats_client: Client, config: NatsResponderConfig) -> None:
        await self.launch(nats_client, config)
        await asyncio.sleep(self.STATUS_INTERVAL_S * 3)
        assert RunnableStatus.RUNNING in self.statuses

    async def traced_ask(self, client: Client, name: str) -> Msg:
        headers = self.headers(self.KEY, self.deadline(self.DEADLINE_S))
        headers[self.TRACEPARENT_HEADER] = self.TRACEPARENT
        return await client.request(self.SUBJECT, self.body(name), timeout=self.TIMEOUT_S, headers=headers)

    async def server_spans(self, recorded_signals: RecordedSignals) -> List[ReadableSpan]:
        async with asyncio.timeout(self.TIMEOUT_S):
            while True:
                found = [span for span in recorded_signals.spans() if span.kind == SpanKind.SERVER]
                if found:
                    return found
                await asyncio.sleep(self.STATUS_INTERVAL_S)

    async def test_a_request_with_a_traceparent_is_handled_in_a_server_span_of_that_trace(
        self, nats_client: Client, config: NatsResponderConfig, recorded_signals: RecordedSignals
    ) -> None:
        await self.launch(nats_client, config)
        await self.traced_ask(nats_client, self.REQUEST_NAME)
        spans = await self.server_spans(recorded_signals)
        assert [span.context.trace_id for span in spans] == [self.TRACE_ID]
        assert spans[0].parent is not None
        assert spans[0].parent.span_id == self.PARENT_SPAN_ID

    async def test_a_handler_failure_sets_the_server_span_status_to_error(
        self, nats_client: Client, config: NatsResponderConfig, recorded_signals: RecordedSignals
    ) -> None:
        await self.launch(nats_client, config)
        await self.traced_ask(nats_client, self.FAILING_NAME)
        spans = await self.server_spans(recorded_signals)
        assert spans[0].status.status_code == StatusCode.ERROR
