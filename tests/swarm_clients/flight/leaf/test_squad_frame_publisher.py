from __future__ import annotations

# Standard library imports
from uuid import UUID, uuid4

# Third-party imports
import pytest
from nats.aio.client import Client, Msg
from nats.errors import TimeoutError as NatsTimeoutError
from opentelemetry.trace import SpanKind

# First-party imports
from swarm_clients.flight.leaf.squad_frame_publisher import SquadFramePublisher
from swarm_nats.models.bus.nats_headers import NatsHeaders
from tests.fakes.signals.recorded_signals import RecordedSignals

SUBJECT_TEMPLATE = "op.{operator_id}.mission.{mission_id}.squad"
FRAME = b"\x82\xa4tick\x01\xa6drones\x90"
OTHER_FRAME = b"\x80"
WAIT_S = 2.0
SETTLE_S = 0.3
OPERATOR_ATTRIBUTE = "operator_id"
MISSION_ATTRIBUTE = "mission_id"
DRONE_ATTRIBUTE = "drone_id"
FRAME_ENCODING = "latin-1"


def a_uuid7() -> UUID:
    raw = bytearray(uuid4().bytes)
    raw[6] = (raw[6] & 0x0F) | 0x70
    raw[8] = (raw[8] & 0x3F) | 0x80
    return UUID(bytes=bytes(raw))


class TestSquadFramePublisher:
    async def test_a_subscriber_receives_exactly_the_published_bytes(self, nats_client: Client) -> None:
        operator_id, mission_id = a_uuid7(), a_uuid7()
        subscription = await nats_client.subscribe(
            SUBJECT_TEMPLATE.format(operator_id=operator_id, mission_id=mission_id)
        )
        await nats_client.flush()
        await SquadFramePublisher(nats_client).publish(operator_id, mission_id, FRAME)
        message: Msg = await subscription.next_msg(timeout=WAIT_S)
        assert message.data == FRAME

    async def test_another_operators_subscriber_sees_nothing(self, nats_client: Client) -> None:
        operator_id, other_operator_id, mission_id = a_uuid7(), a_uuid7(), a_uuid7()
        subscription = await nats_client.subscribe(
            SUBJECT_TEMPLATE.format(operator_id=other_operator_id, mission_id=mission_id)
        )
        await nats_client.flush()
        await SquadFramePublisher(nats_client).publish(operator_id, mission_id, FRAME)
        await nats_client.flush()
        with pytest.raises(NatsTimeoutError):
            await subscription.next_msg(timeout=SETTLE_S)

    async def test_each_publication_reaches_its_own_mission_subject(self, nats_client: Client) -> None:
        operator_id, first_mission, second_mission = a_uuid7(), a_uuid7(), a_uuid7()
        first = await nats_client.subscribe(SUBJECT_TEMPLATE.format(operator_id=operator_id, mission_id=first_mission))
        second = await nats_client.subscribe(
            SUBJECT_TEMPLATE.format(operator_id=operator_id, mission_id=second_mission)
        )
        await nats_client.flush()
        publisher = SquadFramePublisher(nats_client)
        await publisher.publish(operator_id, first_mission, FRAME)
        await publisher.publish(operator_id, second_mission, OTHER_FRAME)
        assert (await first.next_msg(timeout=WAIT_S)).data == FRAME
        assert (await second.next_msg(timeout=WAIT_S)).data == OTHER_FRAME

    @pytest.mark.parametrize("size", [1, 4096])
    async def test_payloads_of_any_size_arrive_unchanged(self, nats_client: Client, size: int) -> None:
        operator_id, mission_id = a_uuid7(), a_uuid7()
        data = (bytes(range(256)) * (size // 256 + 1))[:size]
        subscription = await nats_client.subscribe(
            SUBJECT_TEMPLATE.format(operator_id=operator_id, mission_id=mission_id)
        )
        await nats_client.flush()
        await SquadFramePublisher(nats_client).publish(operator_id, mission_id, data)
        assert (await subscription.next_msg(timeout=WAIT_S)).data == data

    async def test_a_frame_carries_the_trace_context_and_a_producer_span_names_its_mission(
        self, nats_client: Client, recorded_signals: RecordedSignals
    ) -> None:
        operator_id, mission_id = a_uuid7(), a_uuid7()
        subscription = await nats_client.subscribe(
            SUBJECT_TEMPLATE.format(operator_id=operator_id, mission_id=mission_id)
        )
        await nats_client.flush()
        await SquadFramePublisher(nats_client).publish(operator_id, mission_id, FRAME)
        message: Msg = await subscription.next_msg(timeout=WAIT_S)
        assert message.headers is not None
        assert NatsHeaders.TRACE_PARENT in message.headers
        producers = [span for span in recorded_signals.spans() if span.kind == SpanKind.PRODUCER]
        assert len(producers) == 1
        attributes = dict(producers[0].attributes or {})
        assert attributes[OPERATOR_ATTRIBUTE] == str(operator_id)
        assert attributes[MISSION_ATTRIBUTE] == str(mission_id)

    async def test_no_span_attribute_holds_a_drone_or_the_frame_bytes(
        self, nats_client: Client, recorded_signals: RecordedSignals
    ) -> None:
        operator_id, mission_id = a_uuid7(), a_uuid7()
        await SquadFramePublisher(nats_client).publish(operator_id, mission_id, FRAME)
        spans = recorded_signals.spans()
        assert spans
        for span in spans:
            attributes = dict(span.attributes or {})
            assert DRONE_ATTRIBUTE not in attributes
            assert FRAME not in attributes.values()
            assert FRAME.decode(FRAME_ENCODING) not in attributes.values()
