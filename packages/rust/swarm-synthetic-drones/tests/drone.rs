//! Tests of the `MAVLink` state machine of a synthetic Drone.

// The Mission upload frame is the deprecated INT variant on purpose: it is the frame a real autopilot receives.
#![allow(deprecated)]

use mavlink::dialects::common::{
    MavCmd, MavFrame, MavMessage, MavMissionResult, MavModeFlag, MavResult, MavType, COMMAND_LONG_DATA,
    MISSION_COUNT_DATA, MISSION_ITEM_INT_DATA,
};
use swarm_synthetic_drones::drone::{DroneConfig, DroneState, SyntheticDrone};
use swarm_synthetic_drones::route::{distance_m, offset, Position, ARRIVAL_TOLERANCE_M};

const SYSTEM_ID: u8 = 7;
const OTHER_SYSTEM_ID: u8 = 9;
const SPEED_M_S: f32 = 20.0;
const SIDE_M: f32 = 20.0;
const CRUISE_ALTITUDE_M: f32 = 10.0;
const DT_S: f32 = 0.1;
const MAX_TICKS: usize = 5000;
const ITEM_COUNT: u16 = 7;
const LAST_SEQ: u16 = 6;

fn home() -> Position {
    Position {
        lat_e7: 485_000_000,
        lon_e7: 23_000_000,
        altitude_m: 0.0,
    }
}

fn a_drone() -> SyntheticDrone {
    SyntheticDrone::new(DroneConfig {
        system_id: SYSTEM_ID,
        home: home(),
        speed_m_s: SPEED_M_S,
    })
}

/// The seven items: takeoff, a 20 m square of five waypoints, land at home.
fn mission_positions() -> Vec<Position> {
    let up = Position {
        altitude_m: CRUISE_ALTITUDE_M,
        ..home()
    };
    let corner = |north_m: f32, east_m: f32| offset(up, north_m, east_m);
    vec![
        up,
        corner(SIDE_M, 0.0),
        corner(SIDE_M, SIDE_M),
        corner(0.0, SIDE_M),
        corner(0.0, 0.0),
        corner(SIDE_M, 0.0),
        home(),
    ]
}

fn item_command(seq: u16) -> MavCmd {
    match seq {
        0 => MavCmd::MAV_CMD_NAV_TAKEOFF,
        LAST_SEQ => MavCmd::MAV_CMD_NAV_LAND,
        _ => MavCmd::MAV_CMD_NAV_WAYPOINT,
    }
}

fn item(seq: u16, command: MavCmd, position: Position, target_system: u8) -> MavMessage {
    MavMessage::MISSION_ITEM_INT(MISSION_ITEM_INT_DATA {
        target_system,
        target_component: 1,
        seq,
        frame: MavFrame::MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        command,
        x: position.lat_e7,
        y: position.lon_e7,
        z: position.altitude_m,
        autocontinue: 1,
        ..Default::default()
    })
}

fn count(count: u16, target_system: u8) -> MavMessage {
    MavMessage::MISSION_COUNT(MISSION_COUNT_DATA {
        target_system,
        target_component: 1,
        count,
        ..Default::default()
    })
}

fn command(command: MavCmd, param1: f32) -> MavMessage {
    command_for(SYSTEM_ID, command, param1)
}

fn command_for(target_system: u8, command: MavCmd, param1: f32) -> MavMessage {
    MavMessage::COMMAND_LONG(COMMAND_LONG_DATA {
        target_system,
        target_component: 1,
        command,
        param1,
        ..Default::default()
    })
}

fn send(drone: &mut SyntheticDrone, message: &MavMessage) -> Vec<MavMessage> {
    let mut out = Vec::new();
    drone.handle(message, &mut out);
    out
}

fn tick(drone: &mut SyntheticDrone) -> Vec<MavMessage> {
    let mut out = Vec::new();
    drone.tick(DT_S, &mut out);
    out
}

fn command_result(out: &[MavMessage]) -> MavResult {
    match out {
        [MavMessage::COMMAND_ACK(ack)] => ack.result,
        other => panic!("expected one COMMAND_ACK, got {other:?}"),
    }
}

fn mission_result(out: &[MavMessage]) -> MavMissionResult {
    match out {
        [MavMessage::MISSION_ACK(ack)] => ack.mavtype,
        other => panic!("expected one MISSION_ACK, got {other:?}"),
    }
}

fn is_armed(drone: &SyntheticDrone) -> bool {
    let MavMessage::HEARTBEAT(data) = drone.heartbeat() else {
        panic!("not a HEARTBEAT")
    };
    data.base_mode.contains(MavModeFlag::MAV_MODE_FLAG_SAFETY_ARMED)
}

fn upload(drone: &mut SyntheticDrone) -> Vec<MavMessage> {
    let positions = mission_positions();
    let mut out = send(drone, &count(ITEM_COUNT, SYSTEM_ID));
    for (seq, position) in (0..ITEM_COUNT).zip(positions) {
        assert!(matches!(out.as_slice(), [MavMessage::MISSION_REQUEST_INT(request)] if request.seq == seq));
        out = send(drone, &item(seq, item_command(seq), position, SYSTEM_ID));
    }
    out
}

fn armed_with_mission() -> SyntheticDrone {
    let mut drone = a_drone();
    upload(&mut drone);
    send(&mut drone, &command(MavCmd::MAV_CMD_COMPONENT_ARM_DISARM, 1.0));
    drone
}

fn flying() -> SyntheticDrone {
    let mut drone = armed_with_mission();
    send(&mut drone, &command(MavCmd::MAV_CMD_MISSION_START, 0.0));
    drone
}

fn tick_until(drone: &mut SyntheticDrone, state: DroneState) -> Vec<MavMessage> {
    let mut all = Vec::new();
    for _ in 0..MAX_TICKS {
        if drone.state() == state {
            return all;
        }
        all.extend(tick(drone));
    }
    panic!("the drone never reached {state:?}, it is {:?}", drone.state());
}

fn reached(out: &[MavMessage]) -> Vec<u16> {
    out.iter()
        .filter_map(|message| match message {
            MavMessage::MISSION_ITEM_REACHED(data) => Some(data.seq),
            _ => None,
        })
        .collect()
}

#[test]
fn a_new_drone_is_landed_at_home_with_its_system_id() {
    let drone = a_drone();
    assert_eq!(drone.state(), DroneState::Landed);
    assert_eq!(drone.system_id(), SYSTEM_ID);
    assert_eq!(drone.position(), home());
}

#[test]
fn a_mission_count_gives_the_request_of_item_zero() {
    let mut drone = a_drone();
    let out = send(&mut drone, &count(ITEM_COUNT, SYSTEM_ID));
    assert!(matches!(out.as_slice(), [MavMessage::MISSION_REQUEST_INT(request)] if request.seq == 0));
}

#[test]
fn a_full_upload_is_requested_item_by_item_then_accepted() {
    let mut drone = a_drone();
    let out = upload(&mut drone);
    assert_eq!(mission_result(&out), MavMissionResult::MAV_MISSION_ACCEPTED);
}

#[test]
fn an_unsupported_item_command_is_refused() {
    let mut drone = a_drone();
    send(&mut drone, &count(1, SYSTEM_ID));
    let out = send(&mut drone, &item(0, MavCmd::MAV_CMD_NAV_LOITER_TIME, home(), SYSTEM_ID));
    assert_eq!(mission_result(&out), MavMissionResult::MAV_MISSION_UNSUPPORTED);
}

#[test]
fn a_message_for_another_system_gives_no_output() {
    let mut drone = a_drone();
    let out = send(&mut drone, &count(ITEM_COUNT, OTHER_SYSTEM_ID));
    assert_eq!(out.len(), 0);
    let other = command_for(OTHER_SYSTEM_ID, MavCmd::MAV_CMD_COMPONENT_ARM_DISARM, 1.0);
    let out = send(&mut drone, &other);
    assert_eq!(out.len(), 0);
    assert_eq!(drone.state(), DroneState::Landed);
}

#[test]
fn arming_is_accepted_and_the_state_becomes_armed() {
    let mut drone = a_drone();
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_COMPONENT_ARM_DISARM, 1.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_ACCEPTED);
    assert_eq!(drone.state(), DroneState::Armed);
}

#[test]
fn a_mission_start_when_not_armed_is_denied() {
    let mut drone = a_drone();
    upload(&mut drone);
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_MISSION_START, 0.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_DENIED);
    assert_eq!(drone.state(), DroneState::Landed);
}

#[test]
fn a_mission_start_without_a_mission_is_denied() {
    let mut drone = a_drone();
    send(&mut drone, &command(MavCmd::MAV_CMD_COMPONENT_ARM_DISARM, 1.0));
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_MISSION_START, 0.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_DENIED);
    assert_eq!(drone.state(), DroneState::Armed);
}

#[test]
fn a_mission_start_when_armed_with_a_mission_is_accepted_and_flies() {
    let mut drone = armed_with_mission();
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_MISSION_START, 0.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_ACCEPTED);
    assert_eq!(drone.state(), DroneState::Flying);
}

#[test]
fn an_unknown_command_is_unsupported() {
    let mut drone = a_drone();
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_DO_SET_SERVO, 0.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_UNSUPPORTED);
}

#[test]
fn a_flying_drone_emits_a_position_each_tick() {
    let mut drone = flying();
    for _ in 0..5 {
        let out = tick(&mut drone);
        let positions = out
            .iter()
            .filter(|message| matches!(message, MavMessage::GLOBAL_POSITION_INT(_)))
            .count();
        assert_eq!(positions, 1);
    }
}

#[test]
fn the_takeoff_is_reached_when_the_altitude_is_within_tolerance() {
    let mut drone = flying();
    let mut seen = Vec::new();
    for _ in 0..MAX_TICKS {
        seen.extend(reached(&tick(&mut drone)));
        if seen.contains(&0) {
            break;
        }
    }
    assert_eq!(seen.first(), Some(&0));
    assert!((drone.position().altitude_m - CRUISE_ALTITUDE_M).abs() <= ARRIVAL_TOLERANCE_M);
}

#[test]
fn the_items_are_reached_in_order_then_the_drone_lands_and_is_disarmed() {
    let mut drone = flying();
    let out = tick_until(&mut drone, DroneState::Landed);
    assert_eq!(reached(&out), (0..ITEM_COUNT).collect::<Vec<u16>>());
    assert!(!is_armed(&drone));
    assert!(distance_m(drone.position(), home()) <= ARRIVAL_TOLERANCE_M);
}

#[test]
fn a_pause_holds_the_position_and_a_continue_resumes() {
    let mut drone = flying();
    for _ in 0..5 {
        tick(&mut drone);
    }
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_DO_PAUSE_CONTINUE, 0.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_ACCEPTED);
    assert_eq!(drone.state(), DroneState::Holding);
    let held = drone.position();
    for _ in 0..20 {
        tick(&mut drone);
    }
    assert_eq!(drone.position(), held);
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_DO_PAUSE_CONTINUE, 1.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_ACCEPTED);
    assert_eq!(drone.state(), DroneState::Flying);
    tick(&mut drone);
    assert_ne!(drone.position(), held);
}

#[test]
fn a_return_to_launch_returns_then_lands_at_home() {
    let mut drone = flying();
    for _ in 0..30 {
        tick(&mut drone);
    }
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_NAV_RETURN_TO_LAUNCH, 0.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_ACCEPTED);
    assert_eq!(drone.state(), DroneState::Returning);
    tick_until(&mut drone, DroneState::Landed);
    assert!(distance_m(drone.position(), home()) <= ARRIVAL_TOLERANCE_M);
}

#[test]
fn a_land_command_lands_then_the_state_is_landed() {
    let mut drone = flying();
    for _ in 0..30 {
        tick(&mut drone);
    }
    let out = send(&mut drone, &command(MavCmd::MAV_CMD_NAV_LAND, 0.0));
    assert_eq!(command_result(&out), MavResult::MAV_RESULT_ACCEPTED);
    assert_eq!(drone.state(), DroneState::Landing);
    tick_until(&mut drone, DroneState::Landed);
    assert!(drone.position().altitude_m.abs() <= ARRIVAL_TOLERANCE_M);
}

#[test]
fn the_heartbeat_is_a_quadrotor_and_flags_the_armed_state() {
    let mut drone = a_drone();
    let MavMessage::HEARTBEAT(data) = drone.heartbeat() else {
        panic!("not a HEARTBEAT")
    };
    assert_eq!(data.mavtype, MavType::MAV_TYPE_QUADROTOR);
    assert!(!is_armed(&drone));
    send(&mut drone, &command(MavCmd::MAV_CMD_COMPONENT_ARM_DISARM, 1.0));
    assert!(is_armed(&drone));
}
