from __future__ import annotations

# Standard library imports
import time
from typing import Callable

# Third-party imports
from fastapi.testclient import TestClient

# First-party imports
from swarm_live.service.live_codec import LiveCodec  # isort: skip
from swarm_models.enums import LiveOperation, LiveRate, LiveTopicKind  # isort: skip
from swarm_models.live.live_subscription import LiveSubscription  # isort: skip
from tests.swarm_api.v1.live.gateway_stand_in_live_source import GatewayStandInLiveSource  # isort: skip


class TestGatewayLiveRouter:
    LIVE_PATH = "/v1/live"
    WAIT_S = 3.0
    GARBAGE = b"\xc1 not message pack"

    def topic(self) -> str:
        return LiveSubscription.topic_of(GatewayStandInLiveSource.MISSION_ID, LiveTopicKind.SQUAD)

    def subscribe_message(self) -> bytes:
        subscription = LiveSubscription(op=LiveOperation.SUBSCRIBE, topic=self.topic(), rate=LiveRate.FULL)
        return LiveCodec().encode_subscription(subscription)

    def wait_for(self, condition: Callable[[], bool]) -> bool:
        deadline = time.monotonic() + self.WAIT_S
        while time.monotonic() < deadline:
            if condition():
                return True
            time.sleep(0.01)
        return condition()

    def test_a_subscribe_message_joins_with_the_operator_and_the_topic(
        self, make_client: Callable[[bool], TestClient], stand_in_source: GatewayStandInLiveSource
    ) -> None:
        with make_client(True).websocket_connect(self.LIVE_PATH) as socket:
            socket.send_bytes(self.subscribe_message())
            socket.receive_bytes()
            assert stand_in_source.joins == [(GatewayStandInLiveSource.OPERATOR_ID, self.topic())]

    def test_bytes_put_in_the_mailbox_reach_the_client(
        self, make_client: Callable[[bool], TestClient], stand_in_source: GatewayStandInLiveSource
    ) -> None:
        with make_client(True).websocket_connect(self.LIVE_PATH) as socket:
            socket.send_bytes(self.subscribe_message())
            assert socket.receive_bytes() == GatewayStandInLiveSource.FRAME

    def test_an_unreadable_message_is_ignored_and_the_socket_stays_open(
        self, make_client: Callable[[bool], TestClient], stand_in_source: GatewayStandInLiveSource
    ) -> None:
        with make_client(True).websocket_connect(self.LIVE_PATH) as socket:
            socket.send_bytes(self.GARBAGE)
            socket.send_bytes(self.subscribe_message())
            assert socket.receive_bytes() == GatewayStandInLiveSource.FRAME
        assert len(stand_in_source.joins) == 1

    def test_disconnecting_leaves_every_joined_topic(
        self, make_client: Callable[[bool], TestClient], stand_in_source: GatewayStandInLiveSource
    ) -> None:
        with make_client(True).websocket_connect(self.LIVE_PATH) as socket:
            socket.send_bytes(self.subscribe_message())
            socket.receive_bytes()
        assert self.wait_for(lambda: stand_in_source.leaves == [self.topic()])

    def test_the_operator_never_comes_from_the_client_message(
        self, make_client: Callable[[bool], TestClient], stand_in_source: GatewayStandInLiveSource
    ) -> None:
        message = self.GARBAGE + str(GatewayStandInLiveSource.OTHER_OPERATOR_ID).encode()
        with make_client(True).websocket_connect(self.LIVE_PATH) as socket:
            socket.send_bytes(message)
            socket.send_bytes(self.subscribe_message())
            socket.receive_bytes()
        assert stand_in_source.operators == [GatewayStandInLiveSource.OPERATOR_ID]
