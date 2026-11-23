from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_rest.models.config.exceptions import (
    SEInvalidRestConfigException,
    SERestConfigInvalidHost,
    SERestConfigInvalidIdempotencyMaxEntries,
    SERestConfigInvalidIdempotencyTtl,
    SERestConfigInvalidPort,
    SERestConfigInvalidStatusInterval,
)
from swarm_rest.models.config.rest_config import RestConfig


class TestRestConfig:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "host": "127.0.0.1",
        "port": 9000,
        "status_interval_s": 2.5,
        "idempotency_ttl_s": 60.0,
        "idempotency_max_entries": 50,
    }
    DEFAULTS: ClassVar[Dict[str, JsonValue]] = {
        "host": "0.0.0.0",
        "port": 8000,
        "status_interval_s": 5.0,
        "idempotency_ttl_s": 86400.0,
        "idempotency_max_entries": 10000,
    }

    def build(self, **changes: JsonValue) -> RestConfig:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return RestConfig.model_validate(values)

    def test_defaults(self) -> None:
        config = RestConfig()
        assert config.model_dump() == self.DEFAULTS

    def test_full_valid_construction(self) -> None:
        config = self.build()
        assert config.model_dump() == self.VALID

    @pytest.mark.parametrize("name", list(DEFAULTS))
    def test_none_becomes_the_default(self, name: str) -> None:
        assert getattr(self.build(**{name: None}), name) == self.DEFAULTS[name]

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("host", "", SERestConfigInvalidHost),
            ("host", "   ", SERestConfigInvalidHost),
            ("host", "a b", SERestConfigInvalidHost),
            ("host", 3, SERestConfigInvalidHost),
            ("port", 0, SERestConfigInvalidPort),
            ("port", 65536, SERestConfigInvalidPort),
            ("port", -1, SERestConfigInvalidPort),
            ("port", True, SERestConfigInvalidPort),
            ("port", 80.5, SERestConfigInvalidPort),
            ("port", "8000", SERestConfigInvalidPort),
            ("status_interval_s", 0, SERestConfigInvalidStatusInterval),
            ("status_interval_s", -1.0, SERestConfigInvalidStatusInterval),
            ("status_interval_s", True, SERestConfigInvalidStatusInterval),
            ("status_interval_s", "5", SERestConfigInvalidStatusInterval),
            ("idempotency_ttl_s", 0, SERestConfigInvalidIdempotencyTtl),
            ("idempotency_ttl_s", -1.0, SERestConfigInvalidIdempotencyTtl),
            ("idempotency_ttl_s", True, SERestConfigInvalidIdempotencyTtl),
            ("idempotency_ttl_s", "60", SERestConfigInvalidIdempotencyTtl),
            ("idempotency_max_entries", 0, SERestConfigInvalidIdempotencyMaxEntries),
            ("idempotency_max_entries", -1, SERestConfigInvalidIdempotencyMaxEntries),
            ("idempotency_max_entries", True, SERestConfigInvalidIdempotencyMaxEntries),
            ("idempotency_max_entries", 1.5, SERestConfigInvalidIdempotencyMaxEntries),
            ("idempotency_max_entries", "10", SERestConfigInvalidIdempotencyMaxEntries),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize(
        "error",
        [
            SERestConfigInvalidHost,
            SERestConfigInvalidPort,
            SERestConfigInvalidStatusInterval,
            SERestConfigInvalidIdempotencyTtl,
            SERestConfigInvalidIdempotencyMaxEntries,
        ],
    )
    def test_every_field_error_is_a_rest_config_exception(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidRestConfigException)

    def test_the_bounds(self) -> None:
        assert RestConfig.PORT_MIN == 1
        assert RestConfig.PORT_MAX == 65535
        assert RestConfig.IDEMPOTENCY_MAX_ENTRIES_MIN == 1

    @pytest.mark.parametrize("port", [RestConfig.PORT_MIN, RestConfig.PORT_MAX])
    def test_the_bounds_of_port_are_accepted(self, port: int) -> None:
        assert self.build(port=port).port == port

    def test_the_minimum_of_idempotency_max_entries_is_accepted(self) -> None:
        entries = RestConfig.IDEMPOTENCY_MAX_ENTRIES_MIN
        assert self.build(idempotency_max_entries=entries).idempotency_max_entries == entries

    def test_an_integer_is_accepted_as_a_duration(self) -> None:
        assert self.build(status_interval_s=3).status_interval_s == 3.0

    def test_the_host_is_stripped(self) -> None:
        assert self.build(host="  localhost  ").host == "localhost"

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_round_trip(self) -> None:
        config = self.build()
        assert RestConfig.model_validate(config.model_dump()) == config
