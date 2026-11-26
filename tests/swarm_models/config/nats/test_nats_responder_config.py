from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.config.nats.exceptions import (
    SEInvalidNatsResponderConfigException,
    SENatsResponderConfigInvalidIdempotencyBucket,
    SENatsResponderConfigInvalidIdempotencyTtl,
    SENatsResponderConfigInvalidQueueGroup,
    SENatsResponderConfigInvalidReplicas,
    SENatsResponderConfigInvalidStatusInterval,
    SENatsResponderConfigInvalidSubject,
)
from swarm_models.config.nats.nats_responder_config import NatsResponderConfig


class TestNatsResponderConfig:
    REQUIRED: ClassVar[Dict[str, JsonValue]] = {"subject": "swarm.missions.create", "queue_group": "missions"}
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {
        "subject": "swarm.missions.create",
        "queue_group": "missions",
        "colour": "red",
    }
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SENatsResponderConfigInvalidSubject,
        SENatsResponderConfigInvalidQueueGroup,
        SENatsResponderConfigInvalidIdempotencyBucket,
        SENatsResponderConfigInvalidIdempotencyTtl,
        SENatsResponderConfigInvalidReplicas,
        SENatsResponderConfigInvalidStatusInterval,
    ]

    def test_defaults(self) -> None:
        config = NatsResponderConfig.model_validate(self.REQUIRED)
        assert config.subject == "swarm.missions.create"
        assert config.queue_group == "missions"
        assert config.idempotency_bucket == "idempotency"
        assert config.idempotency_ttl_s == 86400.0
        assert config.replicas == 3
        assert config.status_interval_s == 5.0

    def test_full_valid_construction(self) -> None:
        config = NatsResponderConfig(
            subject="swarm.*.create.>",
            queue_group="workers",
            idempotency_bucket="keys_1-b",
            idempotency_ttl_s=60.0,
            replicas=NatsResponderConfig.REPLICAS_MAX,
            status_interval_s=1.5,
        )
        assert config.subject == "swarm.*.create.>"
        assert config.queue_group == "workers"
        assert config.idempotency_bucket == "keys_1-b"
        assert config.idempotency_ttl_s == 60.0
        assert config.replicas == NatsResponderConfig.REPLICAS_MAX
        assert config.status_interval_s == 1.5

    @pytest.mark.parametrize("name", ["idempotency_bucket", "idempotency_ttl_s", "replicas", "status_interval_s"])
    def test_none_becomes_the_default(self, name: str) -> None:
        config = NatsResponderConfig.model_validate({**self.REQUIRED, name: None})
        default = NatsResponderConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("subject", "", SENatsResponderConfigInvalidSubject),
            ("subject", "   ", SENatsResponderConfigInvalidSubject),
            ("subject", None, SENatsResponderConfigInvalidSubject),
            ("subject", 3, SENatsResponderConfigInvalidSubject),
            ("subject", "swarm missions", SENatsResponderConfigInvalidSubject),
            ("subject", "swarm..missions", SENatsResponderConfigInvalidSubject),
            ("subject", ".swarm", SENatsResponderConfigInvalidSubject),
            ("subject", "swarm.", SENatsResponderConfigInvalidSubject),
            ("queue_group", "", SENatsResponderConfigInvalidQueueGroup),
            ("queue_group", "   ", SENatsResponderConfigInvalidQueueGroup),
            ("queue_group", None, SENatsResponderConfigInvalidQueueGroup),
            ("queue_group", 3, SENatsResponderConfigInvalidQueueGroup),
            ("queue_group", "a b", SENatsResponderConfigInvalidQueueGroup),
            ("idempotency_bucket", "", SENatsResponderConfigInvalidIdempotencyBucket),
            ("idempotency_bucket", "a b", SENatsResponderConfigInvalidIdempotencyBucket),
            ("idempotency_bucket", "a.b", SENatsResponderConfigInvalidIdempotencyBucket),
            ("idempotency_bucket", 3, SENatsResponderConfigInvalidIdempotencyBucket),
            ("idempotency_ttl_s", 0, SENatsResponderConfigInvalidIdempotencyTtl),
            ("idempotency_ttl_s", -1.0, SENatsResponderConfigInvalidIdempotencyTtl),
            ("idempotency_ttl_s", True, SENatsResponderConfigInvalidIdempotencyTtl),
            ("idempotency_ttl_s", "60", SENatsResponderConfigInvalidIdempotencyTtl),
            ("replicas", NatsResponderConfig.REPLICAS_MIN - 1, SENatsResponderConfigInvalidReplicas),
            ("replicas", NatsResponderConfig.REPLICAS_MAX + 1, SENatsResponderConfigInvalidReplicas),
            ("replicas", True, SENatsResponderConfigInvalidReplicas),
            ("replicas", 2.5, SENatsResponderConfigInvalidReplicas),
            ("replicas", "3", SENatsResponderConfigInvalidReplicas),
            ("status_interval_s", 0, SENatsResponderConfigInvalidStatusInterval),
            ("status_interval_s", -1.0, SENatsResponderConfigInvalidStatusInterval),
            ("status_interval_s", True, SENatsResponderConfigInvalidStatusInterval),
            ("status_interval_s", "5", SENatsResponderConfigInvalidStatusInterval),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            NatsResponderConfig.model_validate({**self.REQUIRED, name: value})

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_field_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidNatsResponderConfigException)

    @pytest.mark.parametrize("replicas", [NatsResponderConfig.REPLICAS_MIN, NatsResponderConfig.REPLICAS_MAX])
    def test_the_replica_bounds_are_accepted(self, replicas: int) -> None:
        assert NatsResponderConfig.model_validate({**self.REQUIRED, "replicas": replicas}).replicas == replicas

    @pytest.mark.parametrize("name", ["subject", "queue_group"])
    def test_a_missing_required_field_is_refused(self, name: str) -> None:
        data = {key: value for key, value in self.REQUIRED.items() if key != name}
        with pytest.raises(
            (ValidationError, SENatsResponderConfigInvalidSubject, SENatsResponderConfigInvalidQueueGroup)
        ):
            NatsResponderConfig.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            NatsResponderConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_a_subject_with_surrounding_spaces_is_stripped(self) -> None:
        assert NatsResponderConfig(subject="  a.b  ", queue_group="q").subject == "a.b"

    def test_round_trip(self) -> None:
        config = NatsResponderConfig(subject="a.*.>", queue_group="q", replicas=2)
        data: Dict[str, JsonValue] = config.model_dump()
        assert NatsResponderConfig.model_validate(data) == config
