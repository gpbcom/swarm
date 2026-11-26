from __future__ import annotations

# Standard library imports
from typing import ClassVar, List
from uuid import UUID

# Third-party imports
import pytest

# First-party imports
from swarm_live.models.exceptions import SELiveMessageUnreadable  # isort: skip
from swarm_live.service.live_codec import LiveCodec  # isort: skip
from swarm_models.enums import LiveOperation, LiveTopicKind
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.telemetry.enums import DroneState
from swarm_models.telemetry.squad_frame import SquadFrame
from swarm_models.telemetry.telemetry_frame import TelemetryFrame


class TestLiveCodec:
    MISSION_ID: ClassVar[UUID] = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f")
    DRONE_COUNT: ClassVar[int] = 10
    GARBAGE: ClassVar[List[bytes]] = [b"", b"\xc1", b"\xff\xff\xff", b"not msgpack at all"]

    def a_squad_frame(self) -> SquadFrame:
        frames = [
            TelemetryFrame(
                mission_id=self.MISSION_ID,
                drone_id=UUID(f"01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e{0x60 + index:02x}"),
                seq=index,
                t_us=1_000_000 + index,
                lat_e7=485000000 + index,
                lon_e7=22000000 + index,
                altitude_m=50.5 + index,
                speed_m_s=5.0,
                heading_deg=90.0,
                battery_pct=80.0,
                link_quality_pct=95.0,
                state=DroneState.AIRBORNE,
            )
            for index in range(self.DRONE_COUNT)
        ]
        return SquadFrame(mission_id=self.MISSION_ID, t_us=1_000_000, frames=frames)

    def a_subscription(self) -> LiveSubscription:
        topic = LiveSubscription.topic_of(self.MISSION_ID, LiveTopicKind.SQUAD)
        return LiveSubscription(op=LiveOperation.SUBSCRIBE, topic=topic)

    def test_a_squad_frame_of_ten_drones_round_trips(self) -> None:
        codec = LiveCodec()
        squad_frame = self.a_squad_frame()
        data = codec.encode_squad_frame(squad_frame)
        assert isinstance(data, bytes)
        decoded = codec.decode_squad_frame(data)
        assert decoded == squad_frame
        assert len(decoded.frames) == self.DRONE_COUNT

    def test_a_subscription_round_trips(self) -> None:
        codec = LiveCodec()
        subscription = self.a_subscription()
        assert codec.decode_subscription(codec.encode_subscription(subscription)) == subscription

    def test_the_encoding_is_deterministic(self) -> None:
        codec = LiveCodec()
        squad_frame = self.a_squad_frame()
        assert codec.encode_squad_frame(squad_frame) == codec.encode_squad_frame(squad_frame)

    @pytest.mark.parametrize("data", GARBAGE)
    def test_garbage_is_not_a_squad_frame(self, data: bytes) -> None:
        with pytest.raises(SELiveMessageUnreadable):
            LiveCodec().decode_squad_frame(data)

    @pytest.mark.parametrize("data", GARBAGE)
    def test_garbage_is_not_a_subscription(self, data: bytes) -> None:
        with pytest.raises(SELiveMessageUnreadable):
            LiveCodec().decode_subscription(data)

    def test_a_subscription_is_not_a_squad_frame(self) -> None:
        codec = LiveCodec()
        with pytest.raises(SELiveMessageUnreadable):
            codec.decode_squad_frame(codec.encode_subscription(self.a_subscription()))

    def test_a_squad_frame_is_not_a_subscription(self) -> None:
        codec = LiveCodec()
        with pytest.raises(SELiveMessageUnreadable):
            codec.decode_subscription(codec.encode_squad_frame(self.a_squad_frame()))
