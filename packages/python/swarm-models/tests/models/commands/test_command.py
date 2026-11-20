from __future__ import annotations

# Standard library imports
from typing import ClassVar, Dict
from uuid import UUID

# Third-party imports
import pytest
from pydantic import JsonValue, ValidationError

# First-party imports
from swarm_models.models.commands.command import Command
from swarm_models.models.commands.enums import CommandKind, CommandLane
from swarm_models.models.commands.exceptions import (
    SECommandInvalidDroneId,
    SECommandInvalidId,
    SECommandInvalidIssuedBy,
    SECommandInvalidKind,
    SECommandInvalidLane,
    SECommandInvalidMissionId,
    SECommandWrongLane,
    SEInvalidCommandException,
)


class TestCommand:
    COMMAND_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    MISSION_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61"
    ISSUED_BY: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62"
    VERSION_4_ID: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    VALID: ClassVar[Dict[str, JsonValue]] = {
        "id": COMMAND_ID,
        "mission_id": MISSION_ID,
        "drone_id": DRONE_ID,
        "kind": "hold",
        "issued_by": ISSUED_BY,
        "lane": "safety",
    }
    UNKNOWN_KEY: ClassVar[Dict[str, JsonValue]] = {**VALID, "colour": "red"}

    def a_command(self, **changes: JsonValue) -> Command:
        return Command.model_validate({**self.VALID, **changes})

    def test_defaults(self) -> None:
        data = {name: value for name, value in self.VALID.items() if name != "drone_id"}
        assert Command.model_validate(data).drone_id is None

    def test_full_valid_construction(self) -> None:
        command = self.a_command()
        assert command.id == UUID(self.COMMAND_ID)
        assert command.mission_id == UUID(self.MISSION_ID)
        assert command.drone_id == UUID(self.DRONE_ID)
        assert command.kind is CommandKind.HOLD
        assert command.issued_by == UUID(self.ISSUED_BY)
        assert command.lane is CommandLane.SAFETY

    @pytest.mark.parametrize(
        ("name", "error"),
        [
            ("drone_id", None),
            ("id", SECommandInvalidId),
            ("mission_id", SECommandInvalidMissionId),
            ("kind", SECommandInvalidKind),
            ("issued_by", SECommandInvalidIssuedBy),
            ("lane", SECommandInvalidLane),
        ],
    )
    def test_none_becomes_the_default(self, name: str, error: type[Exception] | None) -> None:
        if error is None:
            assert getattr(self.a_command(**{name: None}), name) is None
        else:
            with pytest.raises(error):
                self.a_command(**{name: None})

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("id", VERSION_4_ID, SECommandInvalidId),
            ("id", True, SECommandInvalidId),
            ("id", 1, SECommandInvalidId),
            ("mission_id", True, SECommandInvalidMissionId),
            ("mission_id", 1, SECommandInvalidMissionId),
            ("drone_id", True, SECommandInvalidDroneId),
            ("drone_id", 1, SECommandInvalidDroneId),
            ("kind", "jump", SECommandInvalidKind),
            ("kind", True, SECommandInvalidKind),
            ("kind", 1, SECommandInvalidKind),
            ("issued_by", VERSION_4_ID, SECommandInvalidIssuedBy),
            ("issued_by", True, SECommandInvalidIssuedBy),
            ("issued_by", 1, SECommandInvalidIssuedBy),
            ("lane", "fast", SECommandInvalidLane),
            ("lane", True, SECommandInvalidLane),
            ("lane", 1, SECommandInvalidLane),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        with pytest.raises(error):
            self.a_command(**{name: value})

    def test_rejects_unknown_keys(self) -> None:
        with pytest.raises(ValidationError):
            Command.model_validate(self.UNKNOWN_KEY)

    @pytest.mark.parametrize("kind", ["hold", "abort", "return_home", "manual_control"])
    def test_a_safety_kind_on_the_normal_lane_is_refused(self, kind: str) -> None:
        with pytest.raises(SECommandWrongLane):
            self.a_command(kind=kind, lane="normal")

    @pytest.mark.parametrize("kind", ["hold", "abort", "return_home", "manual_control"])
    def test_a_safety_kind_on_the_safety_lane_is_accepted(self, kind: str) -> None:
        command = self.a_command(kind=kind, lane="safety")
        assert command.lane is CommandLane.SAFETY
        assert command.kind in Command.SAFETY_KINDS

    def test_the_safety_kinds_are_the_four_kinds(self) -> None:
        assert Command.SAFETY_KINDS == frozenset(CommandKind)

    def test_a_hold_of_the_squad_is_accepted(self) -> None:
        command = self.a_command(drone_id=None, kind="hold", lane="safety")
        assert command.drone_id is None
        assert command.kind is CommandKind.HOLD

    def test_a_command_cannot_be_changed(self) -> None:
        command = self.a_command()
        with pytest.raises(ValidationError):
            command.lane = CommandLane.NORMAL

    @pytest.mark.parametrize(
        "error",
        [
            SECommandInvalidId,
            SECommandInvalidMissionId,
            SECommandInvalidDroneId,
            SECommandInvalidKind,
            SECommandInvalidIssuedBy,
            SECommandInvalidLane,
            SECommandWrongLane,
        ],
    )
    def test_the_exceptions_share_the_model_base(self, error: type[Exception]) -> None:
        assert issubclass(error, SEInvalidCommandException)
        assert not issubclass(error, ValueError)

    def test_the_base_exception_is_an_exception_and_not_a_value_error(self) -> None:
        assert issubclass(SEInvalidCommandException, Exception)
        assert not issubclass(SEInvalidCommandException, ValueError)

    def test_round_trip(self) -> None:
        command = self.a_command()
        python_data: Dict[str, JsonValue] = command.model_dump()
        assert Command.model_validate(python_data) == command
        assert Command.model_validate_json(command.model_dump_json()) == command
