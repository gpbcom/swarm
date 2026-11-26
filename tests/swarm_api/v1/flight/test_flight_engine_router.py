from __future__ import annotations

# Standard library imports
import time
from http import HTTPStatus
from typing import ClassVar
from uuid import UUID

# Third-party imports
from fastapi.testclient import TestClient

# First-party imports
from swarm_api.v1.flight.flight_engine_router import FlightEngineRouter
from swarm_models.config.flight_engine.flight_engine_config import FlightEngineConfig
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription
from swarm_service.shared.live.hub.live_hub import LiveHub
from swarm_service.shared.live.live_codec import LiveCodec


class TestFlightEngineRouter:
    PATH: ClassVar[str] = "/v1/live"
    MISSION_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f8001")
    OTHER_MISSION_ID: ClassVar[UUID] = UUID("0190a5b2-7c3e-7d4f-8a1b-2c3d4e5f8002")
    FRAME: ClassVar[bytes] = b"frame-of-the-mission"
    OTHER_FRAME: ClassVar[bytes] = b"frame-of-another-mission"
    GARBAGE: ClassVar[bytes] = b"\xc1\xc1 not messagepack"
    WAIT_S: ClassVar[float] = 5.0
    POLL_S: ClassVar[float] = 0.01
    OPENAPI_PATH: ClassVar[str] = "/v1/openapi.json"
    INFO_KEY: ClassVar[str] = "info"
    TITLE_KEY: ClassVar[str] = "title"

    def a_router(self) -> FlightEngineRouter:
        return FlightEngineRouter(FlightEngineConfig())

    def topic(self, mission_id: UUID) -> str:
        return LiveSubscription.topic_of(mission_id, LiveTopicKind.SQUAD)

    def subscription(self, codec: LiveCodec, mission_id: UUID) -> bytes:
        subscription = LiveSubscription(op=LiveOperation.SUBSCRIBE, topic=self.topic(mission_id))
        return codec.encode_subscription(subscription)

    def watchers(self, client: TestClient, hub: LiveHub, mission_id: UUID) -> int:
        assert client.portal is not None
        return int(client.portal.call(hub.watchers, self.topic(mission_id)))

    def wait_for_watchers(self, client: TestClient, hub: LiveHub, mission_id: UUID, expected: int) -> int:
        deadline = time.monotonic() + self.WAIT_S
        count = self.watchers(client, hub, mission_id)
        while count != expected and time.monotonic() < deadline:
            time.sleep(self.POLL_S)
            count = self.watchers(client, hub, mission_id)
        return count

    def publish(self, client: TestClient, hub: LiveHub, mission_id: UUID, data: bytes) -> None:
        assert client.portal is not None
        client.portal.call(hub.publish, self.topic(mission_id), data)

    def test_a_client_receives_the_bytes_published_for_its_mission(self) -> None:
        router = self.a_router()
        hub, codec = router.hub, router.codec
        with TestClient(router.application()) as client, client.websocket_connect(self.PATH) as socket:
            socket.send_bytes(self.subscription(codec, self.MISSION_ID))
            assert self.wait_for_watchers(client, hub, self.MISSION_ID, 1) == 1
            self.publish(client, hub, self.MISSION_ID, self.FRAME)

            assert socket.receive_bytes() == self.FRAME

    def test_a_client_does_not_receive_the_bytes_of_another_mission(self) -> None:
        router = self.a_router()
        hub, codec = router.hub, router.codec
        with TestClient(router.application()) as client, client.websocket_connect(self.PATH) as socket:
            socket.send_bytes(self.subscription(codec, self.MISSION_ID))
            assert self.wait_for_watchers(client, hub, self.MISSION_ID, 1) == 1
            self.publish(client, hub, self.OTHER_MISSION_ID, self.OTHER_FRAME)
            self.publish(client, hub, self.MISSION_ID, self.FRAME)

            assert socket.receive_bytes() == self.FRAME

    def test_an_unreadable_message_is_ignored_and_the_connection_stays_open(self) -> None:
        router = self.a_router()
        hub, codec = router.hub, router.codec
        with TestClient(router.application()) as client, client.websocket_connect(self.PATH) as socket:
            socket.send_bytes(self.GARBAGE)
            socket.send_bytes(self.subscription(codec, self.MISSION_ID))
            assert self.wait_for_watchers(client, hub, self.MISSION_ID, 1) == 1
            self.publish(client, hub, self.MISSION_ID, self.FRAME)

            assert socket.receive_bytes() == self.FRAME

    def test_the_subscription_is_left_when_the_client_disconnects(self) -> None:
        router = self.a_router()
        hub, codec = router.hub, router.codec
        with TestClient(router.application()) as client:
            with client.websocket_connect(self.PATH) as socket:
                socket.send_bytes(self.subscription(codec, self.MISSION_ID))
                assert self.wait_for_watchers(client, hub, self.MISSION_ID, 1) == 1

            assert self.wait_for_watchers(client, hub, self.MISSION_ID, 0) == 0

    def test_the_application_publishes_its_document_under_v1(self) -> None:
        with TestClient(self.a_router().application()) as client:
            response = client.get(self.OPENAPI_PATH)

        assert response.status_code == HTTPStatus.OK
        assert response.json()[self.INFO_KEY][self.TITLE_KEY] == FlightEngineRouter.TITLE
