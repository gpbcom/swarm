from __future__ import annotations

from typing import ClassVar, Dict, List

import pytest
from pydantic import JsonValue, ValidationError

from swarm_nats.models.config.durable_consumer_config import DurableConsumerConfig
from swarm_nats.models.config.exceptions import (
    SEDurableConsumerConfigInvalidAckWait,
    SEDurableConsumerConfigInvalidBatchSize,
    SEDurableConsumerConfigInvalidDurableName,
    SEDurableConsumerConfigInvalidFetchTimeout,
    SEDurableConsumerConfigInvalidFilterSubject,
    SEDurableConsumerConfigInvalidMaxDeliver,
    SEDurableConsumerConfigInvalidStatusInterval,
    SEDurableConsumerConfigInvalidStream,
    SEInvalidDurableConsumerConfigException,
)


class TestDurableConsumerConfig:
    REQUIRED: ClassVar[Dict[str, JsonValue]] = {"stream": "EVENTS", "durable_name": "projector"}
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {
        "stream": "EVENTS",
        "durable_name": "projector",
        "colour": "red",
    }
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEDurableConsumerConfigInvalidStream,
        SEDurableConsumerConfigInvalidDurableName,
        SEDurableConsumerConfigInvalidFilterSubject,
        SEDurableConsumerConfigInvalidBatchSize,
        SEDurableConsumerConfigInvalidFetchTimeout,
        SEDurableConsumerConfigInvalidAckWait,
        SEDurableConsumerConfigInvalidMaxDeliver,
        SEDurableConsumerConfigInvalidStatusInterval,
    ]

    def test_defaults(self) -> None:
        config = DurableConsumerConfig.model_validate(self.REQUIRED)
        assert config.stream == "EVENTS"
        assert config.durable_name == "projector"
        assert config.filter_subject is None
        assert config.batch_size == 100
        assert config.fetch_timeout_s == 1.0
        assert config.ack_wait_s == 30.0
        assert config.max_deliver == -1
        assert config.status_interval_s == 5.0

    def test_full_valid_construction(self) -> None:
        config = DurableConsumerConfig(
            stream="EVENTS_1",
            durable_name="proj-a",
            filter_subject="events.*.>",
            batch_size=10,
            fetch_timeout_s=0.5,
            ack_wait_s=60.0,
            max_deliver=5,
            status_interval_s=2.5,
        )
        assert config.stream == "EVENTS_1"
        assert config.durable_name == "proj-a"
        assert config.filter_subject == "events.*.>"
        assert config.batch_size == 10
        assert config.fetch_timeout_s == 0.5
        assert config.ack_wait_s == 60.0
        assert config.max_deliver == 5
        assert config.status_interval_s == 2.5

    @pytest.mark.parametrize(
        "name",
        ["filter_subject", "batch_size", "fetch_timeout_s", "ack_wait_s", "max_deliver", "status_interval_s"],
    )
    def test_none_becomes_the_default(self, name: str) -> None:
        config = DurableConsumerConfig.model_validate({**self.REQUIRED, name: None})
        default = DurableConsumerConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("stream", "", SEDurableConsumerConfigInvalidStream),
            ("stream", "   ", SEDurableConsumerConfigInvalidStream),
            ("stream", None, SEDurableConsumerConfigInvalidStream),
            ("stream", 3, SEDurableConsumerConfigInvalidStream),
            ("stream", "a b", SEDurableConsumerConfigInvalidStream),
            ("stream", "a.b", SEDurableConsumerConfigInvalidStream),
            ("durable_name", "", SEDurableConsumerConfigInvalidDurableName),
            ("durable_name", "   ", SEDurableConsumerConfigInvalidDurableName),
            ("durable_name", None, SEDurableConsumerConfigInvalidDurableName),
            ("durable_name", 3, SEDurableConsumerConfigInvalidDurableName),
            ("durable_name", "a b", SEDurableConsumerConfigInvalidDurableName),
            ("durable_name", "a.b", SEDurableConsumerConfigInvalidDurableName),
            ("filter_subject", "", SEDurableConsumerConfigInvalidFilterSubject),
            ("filter_subject", "   ", SEDurableConsumerConfigInvalidFilterSubject),
            ("filter_subject", 3, SEDurableConsumerConfigInvalidFilterSubject),
            ("filter_subject", "a b", SEDurableConsumerConfigInvalidFilterSubject),
            ("filter_subject", "a..b", SEDurableConsumerConfigInvalidFilterSubject),
            ("filter_subject", ".a", SEDurableConsumerConfigInvalidFilterSubject),
            ("filter_subject", "a.", SEDurableConsumerConfigInvalidFilterSubject),
            ("batch_size", DurableConsumerConfig.BATCH_SIZE_MIN - 1, SEDurableConsumerConfigInvalidBatchSize),
            ("batch_size", True, SEDurableConsumerConfigInvalidBatchSize),
            ("batch_size", 1.5, SEDurableConsumerConfigInvalidBatchSize),
            ("batch_size", "10", SEDurableConsumerConfigInvalidBatchSize),
            ("fetch_timeout_s", 0, SEDurableConsumerConfigInvalidFetchTimeout),
            ("fetch_timeout_s", -1.0, SEDurableConsumerConfigInvalidFetchTimeout),
            ("fetch_timeout_s", True, SEDurableConsumerConfigInvalidFetchTimeout),
            ("fetch_timeout_s", "1", SEDurableConsumerConfigInvalidFetchTimeout),
            ("ack_wait_s", 0, SEDurableConsumerConfigInvalidAckWait),
            ("ack_wait_s", -1.0, SEDurableConsumerConfigInvalidAckWait),
            ("ack_wait_s", True, SEDurableConsumerConfigInvalidAckWait),
            ("ack_wait_s", "30", SEDurableConsumerConfigInvalidAckWait),
            ("max_deliver", 0, SEDurableConsumerConfigInvalidMaxDeliver),
            ("max_deliver", -2, SEDurableConsumerConfigInvalidMaxDeliver),
            ("max_deliver", True, SEDurableConsumerConfigInvalidMaxDeliver),
            ("max_deliver", 1.5, SEDurableConsumerConfigInvalidMaxDeliver),
            ("max_deliver", "3", SEDurableConsumerConfigInvalidMaxDeliver),
            ("status_interval_s", 0, SEDurableConsumerConfigInvalidStatusInterval),
            ("status_interval_s", -1.0, SEDurableConsumerConfigInvalidStatusInterval),
            ("status_interval_s", True, SEDurableConsumerConfigInvalidStatusInterval),
            ("status_interval_s", "5", SEDurableConsumerConfigInvalidStatusInterval),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            DurableConsumerConfig.model_validate({**self.REQUIRED, name: value})

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidDurableConsumerConfigException)

    @pytest.mark.parametrize("max_deliver", [-1, 1, 7])
    def test_unlimited_or_positive_max_deliver_is_accepted(self, max_deliver: int) -> None:
        config = DurableConsumerConfig.model_validate({**self.REQUIRED, "max_deliver": max_deliver})
        assert config.max_deliver == max_deliver

    def test_the_batch_size_bound_is_accepted(self) -> None:
        batch_size = DurableConsumerConfig.BATCH_SIZE_MIN
        config = DurableConsumerConfig.model_validate({**self.REQUIRED, "batch_size": batch_size})
        assert config.batch_size == batch_size

    @pytest.mark.parametrize("name", ["stream", "durable_name"])
    def test_a_missing_required_field_is_refused(self, name: str) -> None:
        data = {key: value for key, value in self.REQUIRED.items() if key != name}
        with pytest.raises(
            (ValidationError, SEDurableConsumerConfigInvalidStream, SEDurableConsumerConfigInvalidDurableName)
        ):
            DurableConsumerConfig.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            DurableConsumerConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_a_stream_with_surrounding_spaces_is_stripped(self) -> None:
        assert DurableConsumerConfig(stream="  EVENTS  ", durable_name="d").stream == "EVENTS"

    def test_round_trip(self) -> None:
        config = DurableConsumerConfig(stream="EVENTS", durable_name="d", filter_subject="a.>", max_deliver=3)
        data: Dict[str, JsonValue] = config.model_dump()
        assert DurableConsumerConfig.model_validate(data) == config
