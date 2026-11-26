//! The generated types read the frames and commands that the Python models write.

use serde_json::{json, Value};
use swarm_models::{Command, CommandKind, CommandLane, DroneState, SquadFrame, TelemetryFrame};

const MISSION_ID: &str = "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e5f";

fn telemetry_sample() -> Value {
    json!({
        "mission_id": MISSION_ID,
        "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60",
        "seq": 42,
        "t_us": 1_768_728_600_000_000_i64,
        "lat_e7": 482_000_000,
        "lon_e7": 23_500_000,
        "altitude_m": 35.5,
        "speed_m_s": 8.25,
        "heading_deg": 90.0,
        "battery_pct": 76.5,
        "link_quality_pct": 99.0,
        "state": "airborne"
    })
}

fn command_sample() -> Value {
    json!({
        "id": "01943c5e-8a4b-7d00-8000-000000000001",
        "mission_id": MISSION_ID,
        "drone_id": "01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e60",
        "kind": "hold",
        "issued_by": "01943c5e-8a4b-7d00-8000-000000000002",
        "lane": "safety"
    })
}

#[test]
fn a_telemetry_frame_is_deserialised() {
    let frame: TelemetryFrame = serde_json::from_value(telemetry_sample()).expect("the frame should deserialise");
    assert_eq!(frame.state, DroneState::Airborne);
    assert_eq!(frame.seq, 42);
}

#[test]
fn a_telemetry_frame_round_trips_to_the_same_value() {
    let frame: TelemetryFrame = serde_json::from_value(telemetry_sample()).expect("the frame should deserialise");
    assert_eq!(
        serde_json::to_value(&frame).expect("the frame should serialise"),
        telemetry_sample()
    );
}

#[test]
fn a_telemetry_frame_with_an_unknown_key_is_refused() {
    let mut sample = telemetry_sample();
    sample["payload_state"] = json!("ok");
    assert!(serde_json::from_value::<TelemetryFrame>(sample).is_err());
}

#[test]
fn a_telemetry_frame_with_an_unknown_state_is_refused() {
    let mut sample = telemetry_sample();
    sample["state"] = json!("flying");
    assert!(serde_json::from_value::<TelemetryFrame>(sample).is_err());
}

#[test]
fn a_squad_frame_holds_its_frames() {
    let sample = json!({
        "mission_id": MISSION_ID,
        "t_us": 1_768_728_600_000_000_i64,
        "frames": [telemetry_sample()]
    });
    let squad: SquadFrame = serde_json::from_value(sample).expect("the squad frame should deserialise");
    assert_eq!(squad.frames.len(), 1);
}

#[test]
fn a_command_is_deserialised() {
    let command: Command = serde_json::from_value(command_sample()).expect("the command should deserialise");
    assert_eq!(command.kind, CommandKind::Hold);
    assert_eq!(command.lane, CommandLane::Safety);
}

#[test]
fn a_command_round_trips_to_the_same_value() {
    let command: Command = serde_json::from_value(command_sample()).expect("the command should deserialise");
    assert_eq!(
        serde_json::to_value(&command).expect("the command should serialise"),
        command_sample()
    );
}
