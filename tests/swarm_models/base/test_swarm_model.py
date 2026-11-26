from __future__ import annotations

# Standard library imports
from datetime import UTC, datetime, timedelta, timezone
from typing import ClassVar, List, Tuple
from uuid import UUID

# Third-party imports
import pytest
from pydantic import BaseModel

# First-party imports
from swarm_models.base.swarm_model import SwarmModel


class TestSwarmModel:
    UUID7: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    UUID4: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"

    UUID_REFUSED: ClassVar[List[object]] = [UUID4, UUID(UUID4), "not-a-uuid", "", 7, True, None]
    UTC_REFUSED: ClassVar[List[object]] = [
        datetime(2026, 1, 1, 12, 0, 0),
        "2026-01-01T12:00:00",
        "not-a-date",
        20260101,
        True,
        None,
    ]
    TEXT_REFUSED: ClassVar[List[object]] = ["", "   ", "\t\n", 5, True, b"text", None]
    INT_REFUSED: ClassVar[List[object]] = [True, 1.5, 2.0, "3", None]
    FLOAT_REFUSED: ClassVar[List[object]] = [True, float("nan"), float("inf"), float("-inf"), "1.5", None]

    def check_refusal(self, info: pytest.ExceptionInfo[LookupError], value: object) -> None:
        message = str(info.value)
        assert message.startswith(f"Invalid size: {value!r}.")
        assert "Must be" in message

    def test_it_is_a_pydantic_model_without_fields(self) -> None:
        assert issubclass(SwarmModel, BaseModel)
        assert SwarmModel.model_fields == {}

    def test_it_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValueError):
            SwarmModel.model_validate({"unknown": 1})

    def test_it_forbids_extra_keys_in_its_configuration(self) -> None:
        assert SwarmModel.model_config.get("extra") == "forbid"

    @pytest.mark.parametrize("value", [UUID7, UUID(UUID7)])
    def test_parse_uuid7_accepts_a_version_7_uuid(self, value: object) -> None:
        result = SwarmModel.parse_uuid7("size", value, LookupError)
        assert result == UUID(self.UUID7)
        assert result.version == 7

    @pytest.mark.parametrize("value", UUID_REFUSED)
    def test_parse_uuid7_refuses_other_values(self, value: object) -> None:
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_uuid7("size", value, LookupError)
        self.check_refusal(info, value)

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("2026-01-01T12:00:00Z", datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)),
            ("2026-01-01T14:00:00+02:00", datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)),
            ("2026-01-01T12:00:00.123456+00:00", datetime(2026, 1, 1, 12, 0, 0, 123456, tzinfo=UTC)),
            (
                datetime(2026, 1, 1, 14, 0, 0, 654321, tzinfo=timezone(timedelta(hours=2))),
                datetime(2026, 1, 1, 12, 0, 0, 654321, tzinfo=UTC),
            ),
            (datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC), datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)),
        ],
    )
    def test_parse_utc_returns_the_same_instant_in_utc(self, value: object, expected: datetime) -> None:
        result = SwarmModel.parse_utc("size", value, LookupError)
        assert result == expected
        assert result.tzinfo is UTC
        assert result.microsecond == expected.microsecond

    @pytest.mark.parametrize("value", UTC_REFUSED)
    def test_parse_utc_refuses_other_values(self, value: object) -> None:
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_utc("size", value, LookupError)
        self.check_refusal(info, value)

    @pytest.mark.parametrize("value, expected", [("text", "text"), ("  padded \n", "padded"), ("a b", "a b")])
    def test_parse_text_returns_the_stripped_string(self, value: str, expected: str) -> None:
        assert SwarmModel.parse_text("size", value, LookupError) == expected

    @pytest.mark.parametrize("value", TEXT_REFUSED)
    def test_parse_text_refuses_other_values(self, value: object) -> None:
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_text("size", value, LookupError)
        self.check_refusal(info, value)

    @pytest.mark.parametrize(
        "value, bounds",
        [(5, (None, None)), (0, (0, 10)), (10, (0, 10)), (-3, (None, 0)), (4, (4, None)), (-7, (None, None))],
    )
    def test_parse_int_accepts_an_int_within_bounds(self, value: int, bounds: Tuple[object, object]) -> None:
        minimum, maximum = bounds
        result = SwarmModel.parse_int("size", value, LookupError, minimum=minimum, maximum=maximum)
        assert result == value
        assert type(result) is int

    @pytest.mark.parametrize("value", INT_REFUSED)
    def test_parse_int_refuses_other_types(self, value: object) -> None:
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_int("size", value, LookupError)
        self.check_refusal(info, value)

    @pytest.mark.parametrize("value, bounds", [(-1, (0, 10)), (11, (0, 10)), (3, (4, None)), (1, (None, 0))])
    def test_parse_int_refuses_a_value_out_of_bounds(self, value: int, bounds: Tuple[object, object]) -> None:
        minimum, maximum = bounds
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_int("size", value, LookupError, minimum=minimum, maximum=maximum)
        self.check_refusal(info, value)

    @pytest.mark.parametrize(
        "value, expected, bounds",
        [
            (2, 2.0, (None, None)),
            (1.5, 1.5, (None, None)),
            (0.0, 0.0, (0.0, 1.0)),
            (1.0, 1.0, (0.0, 1.0)),
            (-2.5, -2.5, (None, 0.0)),
        ],
    )
    def test_parse_float_accepts_a_number_within_bounds(
        self, value: object, expected: float, bounds: Tuple[object, object]
    ) -> None:
        minimum, maximum = bounds
        result = SwarmModel.parse_float("size", value, LookupError, minimum=minimum, maximum=maximum)
        assert result == expected
        assert type(result) is float

    def test_parse_float_accepts_the_maximum_unless_it_is_exclusive(self) -> None:
        assert SwarmModel.parse_float("size", 1.0, LookupError, maximum=1.0) == 1.0
        assert SwarmModel.parse_float("size", 0.999, LookupError, maximum=1.0, maximum_exclusive=True) == 0.999

    @pytest.mark.parametrize("value", FLOAT_REFUSED)
    def test_parse_float_refuses_other_values(self, value: object) -> None:
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_float("size", value, LookupError)
        self.check_refusal(info, value)

    @pytest.mark.parametrize("value, bounds", [(-0.1, (0.0, 1.0)), (1.1, (0.0, 1.0)), (5, (None, 4.0))])
    def test_parse_float_refuses_a_value_out_of_bounds(self, value: object, bounds: Tuple[object, object]) -> None:
        minimum, maximum = bounds
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_float("size", value, LookupError, minimum=minimum, maximum=maximum)
        self.check_refusal(info, value)

    def test_parse_float_refuses_the_maximum_when_it_is_exclusive(self) -> None:
        with pytest.raises(LookupError) as info:
            SwarmModel.parse_float("size", 1.0, LookupError, minimum=0.0, maximum=1.0, maximum_exclusive=True)
        self.check_refusal(info, 1.0)
