from __future__ import annotations

from typing import ClassVar, Dict, List, Union
from uuid import UUID

import pytest
from pydantic import JsonValue, ValidationError

from swarm_models.models.telemetry.enums import DroneState
from swarm_models.models.telemetry.exceptions import (
    SEInvalidTelemetryFrameException,
    SETelemetryFrameInvalidAltitudeM,
    SETelemetryFrameInvalidBatteryPct,
    SETelemetryFrameInvalidDroneId,
    SETelemetryFrameInvalidHeadingDeg,
    SETelemetryFrameInvalidLatE7,
    SETelemetryFrameInvalidLinkQualityPct,
    SETelemetryFrameInvalidLonE7,
    SETelemetryFrameInvalidMissionId,
    SETelemetryFrameInvalidSeq,
    SETelemetryFrameInvalidSpeedMS,
    SETelemetryFrameInvalidState,
    SETelemetryFrameInvalidTUs,
)
from swarm_models.models.telemetry.telemetry_frame import TelemetryFrame


class TestTelemetryFrame:
    MISSION_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f"
    DRONE_ID: ClassVar[str] = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60"
    VERSION_4_ID: ClassVar[str] = "3f2b8c1e-5d4a-4b6c-9e7f-1a2b3c4d5e6f"
    FIELDS: ClassVar[List[str]] = [
        "mission_id",
        "drone_id",
        "seq",
        "t_us",
        "lat_e7",
        "lon_e7",
        "altitude_m",
        "speed_m_s",
        "heading_deg",
        "battery_pct",
        "link_quality_pct",
        "state",
    ]
    ERRORS: ClassVar[Dict[str, type[Exception]]] = {
        "mission_id": SETelemetryFrameInvalidMissionId,
        "drone_id": SETelemetryFrameInvalidDroneId,
        "seq": SETelemetryFrameInvalidSeq,
        "t_us": SETelemetryFrameInvalidTUs,
        "lat_e7": SETelemetryFrameInvalidLatE7,
        "lon_e7": SETelemetryFrameInvalidLonE7,
        "altitude_m": SETelemetryFrameInvalidAltitudeM,
        "speed_m_s": SETelemetryFrameInvalidSpeedMS,
        "heading_deg": SETelemetryFrameInvalidHeadingDeg,
        "battery_pct": SETelemetryFrameInvalidBatteryPct,
        "link_quality_pct": SETelemetryFrameInvalidLinkQualityPct,
        "state": SETelemetryFrameInvalidState,
    }
    BOUNDS: ClassVar[Dict[str, Union[int, float]]] = {
        "LAT_E7_MIN": -900000000,
        "LAT_E7_MAX": 900000000,
        "LON_E7_MIN": -1800000000,
        "LON_E7_MAX": 1800000000,
        "HEADING_DEG_MIN": 0,
        "HEADING_DEG_MAX": 360,
        "BATTERY_PCT_MIN": 0,
        "BATTERY_PCT_MAX": 100,
        "LINK_QUALITY_PCT_MIN": 0,
        "LINK_QUALITY_PCT_MAX": 100,
        "SEQ_MIN": 0,
        "T_US_MIN": 0,
        "SPEED_M_S_MIN": 0,
    }

    def valid(self) -> Dict[str, JsonValue]:
        return {
            "mission_id": self.MISSION_ID,
            "drone_id": self.DRONE_ID,
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

    def test_defaults(self) -> None:
        for name in self.FIELDS:
            assert TelemetryFrame.model_fields[name].is_required()
        assert set(TelemetryFrame.model_fields) == set(self.FIELDS)
        with pytest.raises(ValidationError):
            TelemetryFrame.model_validate({})

    def test_full_valid_construction(self) -> None:
        frame = TelemetryFrame.model_validate(self.valid())
        assert frame.mission_id == UUID(self.MISSION_ID)
        assert frame.drone_id == UUID(self.DRONE_ID)
        assert frame.seq == 7
        assert frame.t_us == 1_700_000_000_000_000
        assert frame.lat_e7 == 485_000_000
        assert frame.lon_e7 == 22_000_000
        assert frame.altitude_m == 120.5
        assert frame.speed_m_s == 12.25
        assert frame.heading_deg == 90.0
        assert frame.battery_pct == 87.5
        assert frame.link_quality_pct == 99.0
        assert frame.state is DroneState.AIRBORNE

    @pytest.mark.parametrize("name", FIELDS)
    def test_none_becomes_the_default(self, name: str) -> None:
        """No field has a default, so None is refused with the exception of that field."""
        data = self.valid()
        data[name] = None
        with pytest.raises(self.ERRORS[name]):
            TelemetryFrame.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value", "error"),
        [
            ("mission_id", VERSION_4_ID, SETelemetryFrameInvalidMissionId),
            ("mission_id", "not-a-uuid", SETelemetryFrameInvalidMissionId),
            ("mission_id", 3, SETelemetryFrameInvalidMissionId),
            ("mission_id", True, SETelemetryFrameInvalidMissionId),
            ("drone_id", VERSION_4_ID, SETelemetryFrameInvalidDroneId),
            ("drone_id", "not-a-uuid", SETelemetryFrameInvalidDroneId),
            ("drone_id", True, SETelemetryFrameInvalidDroneId),
            ("seq", -1, SETelemetryFrameInvalidSeq),
            ("seq", True, SETelemetryFrameInvalidSeq),
            ("seq", 1.5, SETelemetryFrameInvalidSeq),
            ("seq", "1", SETelemetryFrameInvalidSeq),
            ("t_us", -1, SETelemetryFrameInvalidTUs),
            ("t_us", True, SETelemetryFrameInvalidTUs),
            ("t_us", 1.5, SETelemetryFrameInvalidTUs),
            ("t_us", "1", SETelemetryFrameInvalidTUs),
            ("lat_e7", -900000001, SETelemetryFrameInvalidLatE7),
            ("lat_e7", 900000001, SETelemetryFrameInvalidLatE7),
            ("lat_e7", True, SETelemetryFrameInvalidLatE7),
            ("lat_e7", 1.5, SETelemetryFrameInvalidLatE7),
            ("lat_e7", "1", SETelemetryFrameInvalidLatE7),
            ("lon_e7", -1800000001, SETelemetryFrameInvalidLonE7),
            ("lon_e7", 1800000001, SETelemetryFrameInvalidLonE7),
            ("lon_e7", True, SETelemetryFrameInvalidLonE7),
            ("lon_e7", 1.5, SETelemetryFrameInvalidLonE7),
            ("lon_e7", "1", SETelemetryFrameInvalidLonE7),
            ("altitude_m", True, SETelemetryFrameInvalidAltitudeM),
            ("altitude_m", float("nan"), SETelemetryFrameInvalidAltitudeM),
            ("altitude_m", float("inf"), SETelemetryFrameInvalidAltitudeM),
            ("altitude_m", float("-inf"), SETelemetryFrameInvalidAltitudeM),
            ("altitude_m", "10", SETelemetryFrameInvalidAltitudeM),
            ("speed_m_s", -0.1, SETelemetryFrameInvalidSpeedMS),
            ("speed_m_s", True, SETelemetryFrameInvalidSpeedMS),
            ("speed_m_s", float("nan"), SETelemetryFrameInvalidSpeedMS),
            ("speed_m_s", float("inf"), SETelemetryFrameInvalidSpeedMS),
            ("speed_m_s", "10", SETelemetryFrameInvalidSpeedMS),
            ("heading_deg", -0.1, SETelemetryFrameInvalidHeadingDeg),
            ("heading_deg", 360.0, SETelemetryFrameInvalidHeadingDeg),
            ("heading_deg", 360, SETelemetryFrameInvalidHeadingDeg),
            ("heading_deg", True, SETelemetryFrameInvalidHeadingDeg),
            ("heading_deg", float("nan"), SETelemetryFrameInvalidHeadingDeg),
            ("heading_deg", float("inf"), SETelemetryFrameInvalidHeadingDeg),
            ("heading_deg", "90", SETelemetryFrameInvalidHeadingDeg),
            ("battery_pct", -0.1, SETelemetryFrameInvalidBatteryPct),
            ("battery_pct", 100.1, SETelemetryFrameInvalidBatteryPct),
            ("battery_pct", True, SETelemetryFrameInvalidBatteryPct),
            ("battery_pct", float("nan"), SETelemetryFrameInvalidBatteryPct),
            ("battery_pct", float("inf"), SETelemetryFrameInvalidBatteryPct),
            ("battery_pct", "50", SETelemetryFrameInvalidBatteryPct),
            ("link_quality_pct", -0.1, SETelemetryFrameInvalidLinkQualityPct),
            ("link_quality_pct", 100.1, SETelemetryFrameInvalidLinkQualityPct),
            ("link_quality_pct", True, SETelemetryFrameInvalidLinkQualityPct),
            ("link_quality_pct", float("nan"), SETelemetryFrameInvalidLinkQualityPct),
            ("link_quality_pct", float("inf"), SETelemetryFrameInvalidLinkQualityPct),
            ("link_quality_pct", "50", SETelemetryFrameInvalidLinkQualityPct),
            ("state", "flying", SETelemetryFrameInvalidState),
            ("state", True, SETelemetryFrameInvalidState),
            ("state", 3, SETelemetryFrameInvalidState),
        ],
    )
    def test_rejects_bad_values(self, name: str, value: JsonValue, error: type[Exception]) -> None:
        data = self.valid()
        data[name] = value
        with pytest.raises(error):
            TelemetryFrame.model_validate(data)

    @pytest.mark.parametrize("key", ["payload_state", "colour"])
    def test_rejects_unknown_keys(self, key: str) -> None:
        data = self.valid()
        data[key] = "x"
        with pytest.raises(ValidationError):
            TelemetryFrame.model_validate(data)

    @pytest.mark.parametrize(
        ("name", "value"),
        [
            ("seq", 0),
            ("t_us", 0),
            ("lat_e7", -900000000),
            ("lat_e7", 900000000),
            ("lon_e7", -1800000000),
            ("lon_e7", 1800000000),
            ("speed_m_s", 0.0),
            ("heading_deg", 0.0),
            ("heading_deg", 359.999),
            ("battery_pct", 0.0),
            ("battery_pct", 100.0),
            ("link_quality_pct", 0.0),
            ("link_quality_pct", 100.0),
        ],
    )
    def test_the_bounds_are_inclusive_except_the_heading_maximum(self, name: str, value: JsonValue) -> None:
        data = self.valid()
        data[name] = value
        assert getattr(TelemetryFrame.model_validate(data), name) == value

    @pytest.mark.parametrize("name", sorted(BOUNDS))
    def test_the_bound_class_variables_have_their_values(self, name: str) -> None:
        assert getattr(TelemetryFrame, name) == self.BOUNDS[name]

    def test_an_int_altitude_becomes_a_float(self) -> None:
        data = self.valid()
        data["altitude_m"] = 100
        frame = TelemetryFrame.model_validate(data)
        assert isinstance(frame.altitude_m, float)
        assert frame.altitude_m == 100.0

    @pytest.mark.parametrize("name", ["speed_m_s", "heading_deg", "battery_pct", "link_quality_pct"])
    def test_an_int_is_accepted_for_a_float_field(self, name: str) -> None:
        data = self.valid()
        data[name] = 5
        frame = TelemetryFrame.model_validate(data)
        assert isinstance(getattr(frame, name), float)

    def test_a_negative_altitude_is_accepted(self) -> None:
        data = self.valid()
        data["altitude_m"] = -12.5
        assert TelemetryFrame.model_validate(data).altitude_m == -12.5

    @pytest.mark.parametrize("state", list(DroneState))
    def test_a_state_is_accepted_as_a_member_or_as_its_value(self, state: DroneState) -> None:
        data = self.valid()
        data["state"] = state.value
        assert TelemetryFrame.model_validate(data).state is state
        data["state"] = state
        assert TelemetryFrame.model_validate(data).state is state

    def test_a_frame_cannot_be_changed(self) -> None:
        frame = TelemetryFrame.model_validate(self.valid())
        with pytest.raises(ValidationError):
            frame.seq = 8

    def test_the_exceptions_share_the_model_base(self) -> None:
        assert issubclass(SEInvalidTelemetryFrameException, Exception)
        assert not issubclass(SEInvalidTelemetryFrameException, ValueError)
        for error in self.ERRORS.values():
            assert issubclass(error, SEInvalidTelemetryFrameException)

    def test_round_trip(self) -> None:
        frame = TelemetryFrame.model_validate(self.valid())
        data: Dict[str, JsonValue] = frame.model_dump()
        assert TelemetryFrame.model_validate(data) == frame
        assert TelemetryFrame.model_validate_json(frame.model_dump_json()) == frame
        assert TelemetryFrame.model_validate(frame.model_dump(mode="json")) == frame
