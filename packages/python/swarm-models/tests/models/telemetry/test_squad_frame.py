from __future__ import annotations

from typing import ClassVar, Dict, List
from uuid import UUID

import pytest
from pydantic import JsonValue, ValidationError

from swarm_models.models.telemetry.exceptions import (
    SEInvalidSquadFrameException,
    SESquadFrameDuplicateDrone,
    SESquadFrameInvalidFrames,
    SESquadFrameInvalidMissionId,
    SESquadFrameInvalidTUs,
    SESquadFrameMissionMismatch,
)
from swarm_models.models.telemetry.squad_frame import SquadFrame
from swarm_models.models.telemetry.telemetry_frame import TelemetryFrame


class TestSquadFrame:
    MISSION_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    OTHER_MISSION_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e61"
    DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    OTHER_DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e62"
    VERSION_4_ID: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    FIELDS: ClassVar[List[str]] = ["mission_id", "t_us", "frames"]
    ERRORS: ClassVar[Dict[str, type[Exception]]] = {
        "mission_id": SESquadFrameInvalidMissionId,
        "t_us": SESquadFrameInvalidTUs,
        "frames": SESquadFrameInvalidFrames,
    }

    def frame(self, mission_id: str, drone_id: str) -> Dict[str, JsonValue]:
        return {
            "mission_id": mission_id,
            "drone_id": drone_id,
            "seq": 7,
            "t_us": 1_700_000_000_000_000,
            "lat_e7": 485_000_000,
            "lon_e7": 22_000_000,
            "altitude_m": 120.5,
            "speed_m_s": 12.25,
            "heading_deg": 90.0,
            "battery_pct": 87.5,
            "link_quality_pct": 99.0,
            "state": "airborne",
        }

    def valid(self) -> Dict[str, JsonValue]:
        return {
            "mission_id": self.MISSION_ID,
            "t_us": 1_700_000_000_000_000,
            "frames": [
                self.frame(self.MISSION_ID, self.DRONE_ID),
                self.frame(self.MISSION_ID, self.OTHER_DRONE_ID),
            ],
        }

    def test_defaults(self) -> None:
        for name in self.FIELDS:
            assert SquadFrame.model_fields[name].is_required()
        assert set(SquadFrame.model_fields) == set(self.FIELDS)
        with pytest.raises(ValidationError):
            SquadFrame.model_validate({})

    def test_full_valid_construction(self) -> None:
        squad = SquadFrame.model_validate(self.valid())
        assert squad.mission_id == UUID(self.MISSION_ID)
        assert squad.t_us == 1_700_000_000_000_000
        assert [frame.drone_id for frame in squad.frames] == [UUID(self.DRONE_ID), UUID(self.OTHER_DRONE_ID)]

    @pytest.mark.parametrize("name", FIELDS)
    def test_none_becomes_the_default(self, name: str) -> None:
        """No field has a default, so None is refused with the exception of that field."""
        data = self.valid()
        data[name] = None
        with pytest.raises(self.ERRORS[name]):
            SquadFrame.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("mission_id", VERSION_4_ID, SESquadFrameInvalidMissionId),
            ("mission_id", "not-a-uuid", SESquadFrameInvalidMissionId),
            ("mission_id", True, SESquadFrameInvalidMissionId),
            ("t_us", -1, SESquadFrameInvalidTUs),
            ("t_us", True, SESquadFrameInvalidTUs),
            ("t_us", 1.5, SESquadFrameInvalidTUs),
            ("t_us", "1", SESquadFrameInvalidTUs),
            ("frames", "frames", SESquadFrameInvalidFrames),
            ("frames", 3, SESquadFrameInvalidFrames),
            ("frames", True, SESquadFrameInvalidFrames),
            ("frames", {"a": 1}, SESquadFrameInvalidFrames),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(error):
            SquadFrame.model_validate(data)

    def test_rejects_unknown_keys(self) -> None:
        data = self.valid()
        data["payload_state"] = "x"
        with pytest.raises(ValidationError):
            SquadFrame.model_validate(data)

    def test_t_us_zero_is_accepted(self) -> None:
        data = self.valid()
        data["t_us"] = 0
        assert SquadFrame.model_validate(data).t_us == 0

    def test_the_t_us_minimum_class_variable_is_zero(self) -> None:
        assert SquadFrame.T_US_MIN == 0

    def test_the_frames_may_be_empty(self) -> None:
        data = self.valid()
        data["frames"] = []
        assert SquadFrame.model_validate(data).frames == []

    def test_frames_built_from_mappings_are_telemetry_frames(self) -> None:
        squad = SquadFrame.model_validate(self.valid())
        assert len(squad.frames) == 2
        assert all(isinstance(frame, TelemetryFrame) for frame in squad.frames)

    def test_frames_given_as_instances_are_kept(self) -> None:
        frames = [TelemetryFrame.model_validate(self.frame(self.MISSION_ID, self.DRONE_ID))]
        squad = SquadFrame.model_validate({"mission_id": self.MISSION_ID, "t_us": 5, "frames": frames})
        assert squad.frames == frames

    def test_a_frame_of_another_mission_is_refused(self) -> None:
        data = self.valid()
        data["frames"] = [self.frame(self.OTHER_MISSION_ID, self.DRONE_ID)]
        with pytest.raises(SESquadFrameMissionMismatch):
            SquadFrame.model_validate(data)

    def test_two_frames_of_the_same_drone_are_refused(self) -> None:
        data = self.valid()
        data["frames"] = [
            self.frame(self.MISSION_ID, self.DRONE_ID),
            self.frame(self.MISSION_ID, self.DRONE_ID),
        ]
        with pytest.raises(SESquadFrameDuplicateDrone):
            SquadFrame.model_validate(data)

    def test_a_bad_frame_is_refused(self) -> None:
        bad = self.frame(self.MISSION_ID, self.DRONE_ID)
        bad["payload_state"] = "x"
        data = self.valid()
        data["frames"] = [bad]
        with pytest.raises(ValidationError):
            SquadFrame.model_validate(data)

    def test_a_squad_frame_cannot_be_changed(self) -> None:
        squad = SquadFrame.model_validate(self.valid())
        with pytest.raises(ValidationError):
            squad.t_us = 1

    def test_the_exceptions_share_the_model_base(self) -> None:
        assert issubclass(SEInvalidSquadFrameException, Exception)
        assert not issubclass(SEInvalidSquadFrameException, ValueError)
        for error in [*self.ERRORS.values(), SESquadFrameMissionMismatch, SESquadFrameDuplicateDrone]:
            assert issubclass(error, SEInvalidSquadFrameException)

    def test_round_trip(self) -> None:
        squad = SquadFrame.model_validate(self.valid())
        data: Dict[str, JsonValue] = squad.model_dump()
        assert SquadFrame.model_validate(data) == squad
        assert SquadFrame.model_validate_json(squad.model_dump_json()) == squad
        assert SquadFrame.model_validate(squad.model_dump(mode="json")) == squad
