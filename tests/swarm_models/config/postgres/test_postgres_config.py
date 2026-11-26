from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict, List

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.config.postgres.exceptions import (
    SEInvalidPostgresConfigException,
    SEPostgresConfigInvalidCommandTimeout,
    SEPostgresConfigInvalidDsnKey,
    SEPostgresConfigInvalidPoolMaxSize,
    SEPostgresConfigInvalidPoolMinSize,
    SEPostgresConfigInvalidStatusInterval,
    SEPostgresConfigPoolSizesInverted,
)
from swarm_models.config.postgres.postgres_config import PostgresConfig


class TestPostgresConfig:
    UNKNOWN_KEY_CONFIGURATION: ClassVar[Dict[str, JsonValue]] = {"colour": "red"}
    FIELD_ERRORS: ClassVar[List[type[Exception]]] = [
        SEPostgresConfigInvalidDsnKey,
        SEPostgresConfigInvalidPoolMinSize,
        SEPostgresConfigInvalidPoolMaxSize,
        SEPostgresConfigInvalidCommandTimeout,
        SEPostgresConfigInvalidStatusInterval,
        SEPostgresConfigPoolSizesInverted,
    ]

    def test_defaults(self) -> None:
        config = PostgresConfig()
        assert config.dsn_key == "SWARM_POSTGRES_DSN"
        assert config.pool_min_size == 1
        assert config.pool_max_size == 5
        assert config.command_timeout_s == 5.0
        assert config.status_interval_s == 5.0

    def test_full_valid_construction(self) -> None:
        config = PostgresConfig(
            dsn_key="  MISSIONS_DSN_2  ",
            pool_min_size=PostgresConfig.POOL_MIN_SIZE_MAX,
            pool_max_size=PostgresConfig.POOL_MAX_SIZE_MAX,
            command_timeout_s=2.5,
            status_interval_s=1.5,
        )
        assert config.dsn_key == "MISSIONS_DSN_2"
        assert config.pool_min_size == PostgresConfig.POOL_MIN_SIZE_MAX
        assert config.pool_max_size == PostgresConfig.POOL_MAX_SIZE_MAX
        assert config.command_timeout_s == 2.5
        assert config.status_interval_s == 1.5

    @pytest.mark.parametrize(
        "name", ["dsn_key", "pool_min_size", "pool_max_size", "command_timeout_s", "status_interval_s"]
    )
    def test_none_becomes_the_default(self, name: str) -> None:
        config = PostgresConfig.model_validate({name: None})
        default = PostgresConfig.model_fields[name].get_default(call_default_factory=True)
        assert getattr(config, name) == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("dsn_key", "", SEPostgresConfigInvalidDsnKey),
            ("dsn_key", "   ", SEPostgresConfigInvalidDsnKey),
            ("dsn_key", 3, SEPostgresConfigInvalidDsnKey),
            ("dsn_key", True, SEPostgresConfigInvalidDsnKey),
            ("dsn_key", "lower_case", SEPostgresConfigInvalidDsnKey),
            ("dsn_key", "1_STARTS_WITH_DIGIT", SEPostgresConfigInvalidDsnKey),
            ("dsn_key", "HAS-HYPHEN", SEPostgresConfigInvalidDsnKey),
            ("dsn_key", "HAS SPACE", SEPostgresConfigInvalidDsnKey),
            ("pool_min_size", PostgresConfig.POOL_MIN_SIZE_MIN - 1, SEPostgresConfigInvalidPoolMinSize),
            ("pool_min_size", PostgresConfig.POOL_MIN_SIZE_MAX + 1, SEPostgresConfigInvalidPoolMinSize),
            ("pool_min_size", True, SEPostgresConfigInvalidPoolMinSize),
            ("pool_min_size", 1.5, SEPostgresConfigInvalidPoolMinSize),
            ("pool_min_size", "1", SEPostgresConfigInvalidPoolMinSize),
            ("pool_max_size", PostgresConfig.POOL_MAX_SIZE_MIN - 1, SEPostgresConfigInvalidPoolMaxSize),
            ("pool_max_size", PostgresConfig.POOL_MAX_SIZE_MAX + 1, SEPostgresConfigInvalidPoolMaxSize),
            ("pool_max_size", True, SEPostgresConfigInvalidPoolMaxSize),
            ("pool_max_size", 2.5, SEPostgresConfigInvalidPoolMaxSize),
            ("pool_max_size", "5", SEPostgresConfigInvalidPoolMaxSize),
            ("command_timeout_s", 0, SEPostgresConfigInvalidCommandTimeout),
            ("command_timeout_s", -1.0, SEPostgresConfigInvalidCommandTimeout),
            ("command_timeout_s", True, SEPostgresConfigInvalidCommandTimeout),
            ("command_timeout_s", "5", SEPostgresConfigInvalidCommandTimeout),
            ("status_interval_s", 0, SEPostgresConfigInvalidStatusInterval),
            ("status_interval_s", -1.0, SEPostgresConfigInvalidStatusInterval),
            ("status_interval_s", True, SEPostgresConfigInvalidStatusInterval),
            ("status_interval_s", "5", SEPostgresConfigInvalidStatusInterval),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            PostgresConfig.model_validate({name: value})

    @pytest.mark.parametrize("error", FIELD_ERRORS)
    def test_the_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidPostgresConfigException)

    @pytest.mark.parametrize("size", [PostgresConfig.POOL_MIN_SIZE_MIN, PostgresConfig.POOL_MIN_SIZE_MAX])
    def test_the_minimum_pool_bounds_are_accepted(self, size: int) -> None:
        data: Dict[str, JsonValue] = {"pool_min_size": size, "pool_max_size": PostgresConfig.POOL_MAX_SIZE_MAX}
        assert PostgresConfig.model_validate(data).pool_min_size == size

    @pytest.mark.parametrize("size", [PostgresConfig.POOL_MAX_SIZE_MIN, PostgresConfig.POOL_MAX_SIZE_MAX])
    def test_the_maximum_pool_bounds_are_accepted(self, size: int) -> None:
        data: Dict[str, JsonValue] = {"pool_min_size": PostgresConfig.POOL_MIN_SIZE_MIN, "pool_max_size": size}
        assert PostgresConfig.model_validate(data).pool_max_size == size

    def test_a_minimum_pool_above_the_maximum_is_refused(self) -> None:
        with pytest.raises(SEPostgresConfigPoolSizesInverted):
            PostgresConfig(pool_min_size=6, pool_max_size=5)

    def test_equal_pool_sizes_are_accepted(self) -> None:
        config = PostgresConfig(pool_min_size=3, pool_max_size=3)
        assert config.pool_min_size == config.pool_max_size

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            PostgresConfig.model_validate(self.UNKNOWN_KEY_CONFIGURATION)

    def test_round_trip(self) -> None:
        config = PostgresConfig(dsn_key="OTHER_DSN", pool_min_size=2, pool_max_size=8, command_timeout_s=3.0)
        data: Dict[str, JsonValue] = config.model_dump()
        assert PostgresConfig.model_validate(data) == config
