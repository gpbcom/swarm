from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.enums import LiveOperation, LiveRate, LiveTopicKind
from swarm_models.live.exceptions import (
    SEInvalidLiveSubscriptionException,
    SELiveSubscriptionInvalidOp,
    SELiveSubscriptionInvalidRate,
    SELiveSubscriptionInvalidTopic,
)
from swarm_models.live.live_subscription import LiveSubscription


class TestLiveSubscription:
    MISSION_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    VERSION_4_ID: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    TOPIC: ClassVar[str] = f"mission/{MISSION_ID}/{LiveTopicKind.SQUAD.value}"
    OP_FIELD: ClassVar[str] = "op"
    TOPIC_FIELD: ClassVar[str] = "topic"
    RATE_FIELD: ClassVar[str] = "rate"
    VALID: ClassVar[Dict[str, JsonValue]] = {
        OP_FIELD: LiveOperation.SUBSCRIBE.value,
        TOPIC_FIELD: TOPIC,
        RATE_FIELD: LiveRate.FULL.value,
    }
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}

    def a_subscription(self, **changes: JsonValue) -> LiveSubscription:
        return LiveSubscription.model_validate({**self.VALID, **changes})

    def test_defaults(self) -> None:
        data = {name: value for name, value in self.VALID.items() if name != self.RATE_FIELD}
        assert LiveSubscription.model_validate(data).rate is LiveRate.FULL

    def test_full_valid_construction(self) -> None:
        subscription = self.a_subscription()
        assert subscription.op is LiveOperation.SUBSCRIBE
        assert subscription.topic == self.TOPIC
        assert subscription.rate is LiveRate.FULL

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            (RATE_FIELD, None),
            (OP_FIELD, SELiveSubscriptionInvalidOp),
            (TOPIC_FIELD, SELiveSubscriptionInvalidTopic),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception] | None) -> None:
        if error is None:
            assert getattr(self.a_subscription(**{name: None}), name) is LiveRate.FULL
        else:
            with pytest.raises(error):
                self.a_subscription(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            (OP_FIELD, "unsubscribe", SELiveSubscriptionInvalidOp),
            (OP_FIELD, True, SELiveSubscriptionInvalidOp),
            (OP_FIELD, 1, SELiveSubscriptionInvalidOp),
            (TOPIC_FIELD, True, SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, 1, SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, "", SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, f"mission/{MISSION_ID}/alerts", SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, f"mission/not-a-uuid/{LiveTopicKind.SQUAD.value}", SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, f"mission/{VERSION_4_ID}/{LiveTopicKind.SQUAD.value}", SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, f"mission/{MISSION_ID}", SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, f"mission/{MISSION_ID}/{LiveTopicKind.SQUAD.value}/extra", SELiveSubscriptionInvalidTopic),
            (TOPIC_FIELD, f"fleet/{MISSION_ID}/{LiveTopicKind.SQUAD.value}", SELiveSubscriptionInvalidTopic),
            (RATE_FIELD, "slow", SELiveSubscriptionInvalidRate),
            (RATE_FIELD, True, SELiveSubscriptionInvalidRate),
            (RATE_FIELD, 1, SELiveSubscriptionInvalidRate),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.a_subscription(**{name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            LiveSubscription.model_validate(self.UNKNOWN_KEY)

    def test_a_subscription_without_a_topic_is_refused(self) -> None:
        data = {name: value for name, value in self.VALID.items() if name != self.TOPIC_FIELD}
        with pytest.raises(ValidationError):
            LiveSubscription.model_validate(data)

    def test_a_subscription_cannot_be_changed(self) -> None:
        subscription = self.a_subscription()
        with pytest.raises(ValidationError):
            subscription.rate = LiveRate.FULL

    def test_the_mission_and_the_kind_are_read_from_the_topic(self) -> None:
        subscription = self.a_subscription()
        assert subscription.mission() == UUID(self.MISSION_ID)
        assert subscription.kind() is LiveTopicKind.SQUAD

    def test_topic_of_round_trips_with_mission_and_kind(self) -> None:
        mission_id = UUID(self.MISSION_ID)
        topic = LiveSubscription.topic_of(mission_id, LiveTopicKind.SQUAD)
        assert topic == self.TOPIC
        subscription = self.a_subscription(topic=topic)
        assert subscription.mission() == mission_id
        assert subscription.kind() is LiveTopicKind.SQUAD

    @pytest.mark.parametrize(
        "error",
        [SELiveSubscriptionInvalidOp, SELiveSubscriptionInvalidTopic, SELiveSubscriptionInvalidRate],
    )
    def test_the_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidLiveSubscriptionException)
        assert not issubclass(error, ValueError)

    def test_round_trip(self) -> None:
        subscription = self.a_subscription()
        python_data: Dict[str, JsonValue] = subscription.model_dump()
        assert LiveSubscription.model_validate(python_data) == subscription
        assert LiveSubscription.model_validate_json(subscription.model_dump_json()) == subscription
