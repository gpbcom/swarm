from __future__ import annotations

from typing import ClassVar, Dict

import pytest
from pydantic import JsonValue, ValidationError

from simulator.models.commands.exceptions import (
    SEMavlinkCommandSpecInvalidCommandId,
    SEMavlinkCommandSpecInvalidParam1,
)
from simulator.models.commands.mavlink_command_spec import MavlinkCommandSpec


class TestMavlinkCommandSpec:
    VALID: ClassVar[Dict[str, JsonValue]] = {"command_id": 193, "param1": 1.5}
    REQUIRED: ClassVar[Dict[str, JsonValue]] = {"command_id": 20}
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {"command_id": 20, "colour": "red"}

    def test_defaults(self) -> None:
        spec = MavlinkCommandSpec.model_validate(self.REQUIRED)
        assert spec.command_id == 20
        assert spec.param1 == 0.0

    def test_full_valid_construction(self) -> None:
        spec = MavlinkCommandSpec(command_id=193, param1=1.5)
        assert spec.command_id == 193
        assert spec.param1 == 1.5

    def test_none_becomes_the_default(self) -> None:
        spec = MavlinkCommandSpec.model_validate({**self.REQUIRED, "param1": None})
        default = MavlinkCommandSpec.model_fields["param1"].get_default(call_default_factory=True)
        assert spec.param1 == default

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("command_id", -1, SEMavlinkCommandSpecInvalidCommandId),
            ("command_id", 65536, SEMavlinkCommandSpecInvalidCommandId),
            ("command_id", True, SEMavlinkCommandSpecInvalidCommandId),
            ("command_id", 1.5, SEMavlinkCommandSpecInvalidCommandId),
            ("command_id", "20", SEMavlinkCommandSpecInvalidCommandId),
            ("command_id", None, SEMavlinkCommandSpecInvalidCommandId),
            ("param1", float("nan"), SEMavlinkCommandSpecInvalidParam1),
            ("param1", float("inf"), SEMavlinkCommandSpecInvalidParam1),
            ("param1", float("-inf"), SEMavlinkCommandSpecInvalidParam1),
            ("param1", True, SEMavlinkCommandSpecInvalidParam1),
            ("param1", "1.0", SEMavlinkCommandSpecInvalidParam1),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            MavlinkCommandSpec.model_validate({**self.REQUIRED, name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            MavlinkCommandSpec.model_validate(self.UNKNOWN_KEY)

    def test_round_trip(self) -> None:
        spec = MavlinkCommandSpec.model_validate(self.VALID)
        assert MavlinkCommandSpec.model_validate(spec.model_dump()) == spec
        assert MavlinkCommandSpec.model_validate_json(spec.model_dump_json()) == spec

    @pytest.mark.parametrize("command_id", [0, 65535])
    def test_the_bounds_are_accepted(self, command_id: int) -> None:
        spec = MavlinkCommandSpec.model_validate({"command_id": command_id})
        assert spec.command_id == command_id

    def test_an_integer_param1_becomes_a_float(self) -> None:
        spec = MavlinkCommandSpec.model_validate({**self.REQUIRED, "param1": 2})
        assert spec.param1 == 2.0
        assert isinstance(spec.param1, float)

    def test_a_spec_is_frozen(self) -> None:
        spec = MavlinkCommandSpec.model_validate(self.REQUIRED)
        with pytest.raises(ValidationError):
            spec.command_id = 21
