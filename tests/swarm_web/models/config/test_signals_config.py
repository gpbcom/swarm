from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_web.models.config.exceptions import (
    SEInvalidSignalsConfigException,
    SESignalsConfigInvalidCell,
    SESignalsConfigInvalidEnabled,
    SESignalsConfigInvalidEndpoint,
    SESignalsConfigInvalidMetricsInterval,
    SESignalsConfigInvalidRedactionsPath,
    SESignalsConfigInvalidServiceName,
)
from swarm_web.models.config.signals_config import SignalsConfig


class TestSignalsConfig:
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "enabled": True,
        "endpoint": "https://collector.example.org:4318",
        "service_name": "swarm-gateway",
        "cell": "paris",
        "metrics_interval_s": 15.5,
        "redactions_path": "conf/signal_redactions.yaml",
    }
    DEFAULTS: ClassVar[Dict[str, JsonValue]] = {
        "enabled": False,
        "endpoint": "http://otel-collector:4318",
        "service_name": "swarm",
        "cell": "local",
        "metrics_interval_s": 60.0,
        "redactions_path": None,
    }

    def build(self, **changes: JsonValue) -> SignalsConfig:
        values: Dict[str, JsonValue] = dict(self.VALID)
        values.update(changes)
        return SignalsConfig.model_validate(values)

    def test_defaults(self) -> None:
        assert SignalsConfig().model_dump() == self.DEFAULTS

    def test_full_valid_construction(self) -> None:
        assert self.build().model_dump() == self.VALID

    @pytest.mark.parametrize("name", list(DEFAULTS))
    def test_none_becomes_the_default(self, name: str) -> None:
        assert getattr(self.build(**{name: None}), name) == self.DEFAULTS[name]

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("enabled", "yes", SESignalsConfigInvalidEnabled),
            ("enabled", 1, SESignalsConfigInvalidEnabled),
            ("endpoint", "", SESignalsConfigInvalidEndpoint),
            ("endpoint", "   ", SESignalsConfigInvalidEndpoint),
            ("endpoint", "collector:4318", SESignalsConfigInvalidEndpoint),
            ("endpoint", "ftp://collector:4318", SESignalsConfigInvalidEndpoint),
            ("endpoint", 4318, SESignalsConfigInvalidEndpoint),
            ("service_name", "", SESignalsConfigInvalidServiceName),
            ("service_name", "  ", SESignalsConfigInvalidServiceName),
            ("service_name", 3, SESignalsConfigInvalidServiceName),
            ("cell", "", SESignalsConfigInvalidCell),
            ("cell", "  ", SESignalsConfigInvalidCell),
            ("cell", 3, SESignalsConfigInvalidCell),
            ("metrics_interval_s", 0, SESignalsConfigInvalidMetricsInterval),
            ("metrics_interval_s", -1.0, SESignalsConfigInvalidMetricsInterval),
            ("metrics_interval_s", True, SESignalsConfigInvalidMetricsInterval),
            ("metrics_interval_s", "60", SESignalsConfigInvalidMetricsInterval),
            ("redactions_path", "", SESignalsConfigInvalidRedactionsPath),
            ("redactions_path", "  ", SESignalsConfigInvalidRedactionsPath),
            ("redactions_path", 3, SESignalsConfigInvalidRedactionsPath),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.build(**{name: value})

    @pytest.mark.parametrize(
        "error",
        [
            SESignalsConfigInvalidEnabled,
            SESignalsConfigInvalidEndpoint,
            SESignalsConfigInvalidServiceName,
            SESignalsConfigInvalidCell,
            SESignalsConfigInvalidMetricsInterval,
            SESignalsConfigInvalidRedactionsPath,
        ],
    )
    def test_every_field_error_is_a_signals_config_exception(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidSignalsConfigException)

    def test_the_strings_are_stripped(self) -> None:
        config = self.build(endpoint="  http://a:1  ", service_name=" s ", cell=" c ", redactions_path=" p.yaml ")
        assert (config.endpoint, config.service_name, config.cell, config.redactions_path) == (
            "http://a:1",
            "s",
            "c",
            "p.yaml",
        )

    def test_an_integer_is_accepted_as_a_duration(self) -> None:
        assert self.build(metrics_interval_s=3).metrics_interval_s == 3.0

    def test_a_loaded_configuration_is_frozen(self) -> None:
        config = self.build()
        with pytest.raises(ValidationError):
            config.enabled = False

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            self.build(extra=1)

    def test_round_trip(self) -> None:
        config = self.build()
        assert SignalsConfig.model_validate(config.model_dump()) == config
