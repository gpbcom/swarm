//! Tests of the swarm-synthetic-drones binary over UDP.
#![allow(deprecated)]
#![allow(
    clippy::cast_possible_truncation,
    clippy::cast_lossless,
    clippy::cast_precision_loss,
    clippy::cast_sign_loss
)]

use std::io::{BufRead, BufReader};
use std::net::UdpSocket;
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

use mavlink::dialects::common::{
    MavAutopilot, MavCmd, MavComponent, MavFrame, MavMessage, MavMissionType, MavModeFlag, MavState, MavType,
    COMMAND_LONG_DATA, HEARTBEAT_DATA, MISSION_COUNT_DATA, MISSION_ITEM_INT_DATA,
};
use mavlink::{MavConnection, MavHeader};

const BIN: &str = env!("CARGO_BIN_EXE_swarm-synthetic-drones");
const COUNT: u8 = 3;
const SYSTEM_ID_BASE: u8 = 1;
const HOME_LAT_E7: i32 = 473_977_420;
const HOME_LON_E7: i32 = 85_455_940;
const SPACING_M: f64 = 5.0;
const SQUARE_M: f64 = 20.0;
const REACHED_DEADLINE: Duration = Duration::from_secs(30);
const READY_DEADLINE: Duration = Duration::from_secs(20);
const RECV_TIMEOUT: Duration = Duration::from_secs(10);
const METRES_PER_DEGREE: f64 = 111_320.0;

struct Fleet {
    child: Child,
    base_port: u16,
}

impl Drop for Fleet {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

type Link = Box<dyn MavConnection<MavMessage> + Sync + Send>;

fn free_base_port() -> u16 {
    for attempt in 0..50u16 {
        let base = 30_000 + (std::process::id() as u16 % 2_000) * 10 + attempt * 13;
        let bound: Vec<UdpSocket> = (0..COUNT as u16)
            .filter_map(|i| UdpSocket::bind(("127.0.0.1", base + i)).ok())
            .collect();
        if bound.len() == COUNT as usize {
            return base;
        }
    }
    panic!("no free base port");
}

fn spawn(base_port: u16) -> Option<Fleet> {
    let child = Command::new(BIN)
        .args(["--count", &COUNT.to_string()])
        .args(["--base-port", &base_port.to_string()])
        .args(["--speed-m-s", "50", "--tick-ms", "20"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .expect("the binary starts");
    let mut fleet = Fleet { child, base_port };
    let stdout = fleet.child.stdout.take().expect("piped stdout");
    let (sender, receiver) = std::sync::mpsc::channel();
    std::thread::spawn(move || {
        for line in BufReader::new(stdout).lines().map_while(Result::ok) {
            if sender.send(line).is_err() {
                break;
            }
        }
    });
    let deadline = Instant::now() + READY_DEADLINE;
    while let Some(left) = deadline.checked_duration_since(Instant::now()) {
        match receiver.recv_timeout(left) {
            Ok(line) if line.trim() == "ready" => return Some(fleet),
            Ok(_) => {}
            Err(_) => return None,
        }
    }
    None
}

fn start_fleet() -> Fleet {
    for _ in 0..5 {
        if let Some(fleet) = spawn(free_base_port()) {
            return fleet;
        }
    }
    panic!("the fleet never printed ready");
}

fn connect(port: u16) -> Link {
    Box::new(mavlink::connect::<MavMessage>(&format!("udpout:127.0.0.1:{port}")).expect("udpout connects"))
}

fn gcs_header() -> MavHeader {
    MavHeader {
        system_id: 255,
        component_id: MavComponent::MAV_COMP_ID_MISSIONPLANNER as u8,
        sequence: 0,
    }
}

fn send(link: &Link, message: &MavMessage) {
    link.send(&gcs_header(), message).expect("send");
}

fn gcs_heartbeat() -> MavMessage {
    MavMessage::HEARTBEAT(HEARTBEAT_DATA {
        custom_mode: 0,
        mavtype: MavType::MAV_TYPE_GCS,
        autopilot: MavAutopilot::MAV_AUTOPILOT_INVALID,
        base_mode: MavModeFlag::empty(),
        system_status: MavState::MAV_STATE_ACTIVE,
        mavlink_version: 3,
    })
}

fn recv_until<T>(
    link: &Link,
    deadline: Duration,
    mut pick: impl FnMut(MavHeader, MavMessage) -> Option<T>,
) -> Option<T> {
    let end = Instant::now() + deadline;
    while Instant::now() < end {
        if let Ok((header, message)) = link.recv() {
            if let Some(found) = pick(header, message) {
                return Some(found);
            }
        }
    }
    None
}

fn offset(lat_e7: i32, lon_e7: i32, north_m: f64, east_m: f64) -> (i32, i32) {
    let lat = lat_e7 as f64 / 1e7;
    let dlat = north_m / METRES_PER_DEGREE;
    let dlon = east_m / (METRES_PER_DEGREE * lat.to_radians().cos());
    (
        lat_e7 + (dlat * 1e7).round() as i32,
        lon_e7 + (dlon * 1e7).round() as i32,
    )
}

fn item(system: u8, seq: u16, command: MavCmd, lat_e7: i32, lon_e7: i32) -> MavMessage {
    MavMessage::MISSION_ITEM_INT(MISSION_ITEM_INT_DATA {
        param1: 0.0,
        param2: 0.0,
        param3: 0.0,
        param4: 0.0,
        x: lat_e7,
        y: lon_e7,
        z: 20.0,
        seq,
        command,
        target_system: system,
        target_component: 0,
        frame: MavFrame::MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        current: 0,
        autocontinue: 1,
        mission_type: MavMissionType::MAV_MISSION_TYPE_MISSION,
    })
}

fn square(system: u8, index: usize) -> Vec<MavMessage> {
    let (home_lat, home_lon) = offset(HOME_LAT_E7, HOME_LON_E7, 0.0, SPACING_M * index as f64);
    let corners = [
        (0.0, 0.0),
        (SQUARE_M, 0.0),
        (SQUARE_M, SQUARE_M),
        (0.0, SQUARE_M),
        (0.0, 0.0),
    ];
    let mut items = vec![item(system, 0, MavCmd::MAV_CMD_NAV_TAKEOFF, home_lat, home_lon)];
    for (n, (north, east)) in corners.iter().enumerate() {
        let (lat, lon) = offset(home_lat, home_lon, *north, *east);
        items.push(item(system, 1 + n as u16, MavCmd::MAV_CMD_NAV_WAYPOINT, lat, lon));
    }
    items.push(item(system, 6, MavCmd::MAV_CMD_NAV_LAND, home_lat, home_lon));
    items
}

fn command(system: u8, command: MavCmd, param1: f32) -> MavMessage {
    MavMessage::COMMAND_LONG(COMMAND_LONG_DATA {
        param1,
        param2: 0.0,
        param3: 0.0,
        param4: 0.0,
        param5: 0.0,
        param6: 0.0,
        param7: 0.0,
        command,
        target_system: system,
        target_component: 0,
        confirmation: 0,
    })
}

fn upload(link: &Link, system: u8, items: &[MavMessage]) {
    send(
        link,
        &MavMessage::MISSION_COUNT(MISSION_COUNT_DATA {
            count: items.len() as u16,
            target_system: system,
            target_component: 0,
            mission_type: MavMissionType::MAV_MISSION_TYPE_MISSION,
            ..Default::default()
        }),
    );
    let acked = recv_until(link, RECV_TIMEOUT, |_, message| match message {
        MavMessage::MISSION_REQUEST_INT(request) => {
            send(link, &items[request.seq as usize]);
            None
        }
        MavMessage::MISSION_REQUEST(request) => {
            send(link, &items[request.seq as usize]);
            None
        }
        MavMessage::MISSION_ACK(_) => Some(()),
        _ => None,
    });
    assert!(acked.is_some(), "no MISSION_ACK for system {system}");
}

#[test]
fn each_drone_answers_with_its_own_system_id() {
    let fleet = start_fleet();
    for i in 0..COUNT {
        let link = connect(fleet.base_port + i as u16);
        send(&link, &gcs_heartbeat());
        let expected = SYSTEM_ID_BASE + i;
        let seen = recv_until(&link, RECV_TIMEOUT, |header, message| match message {
            MavMessage::HEARTBEAT(_) if header.system_id == u32::from(expected) => Some(()),
            _ => None,
        });
        assert!(seen.is_some(), "no heartbeat from system {expected}");
    }
}

#[test]
fn each_drone_flies_a_square_mission_and_reports_every_item() {
    let fleet = start_fleet();
    for i in 0..COUNT {
        let system = SYSTEM_ID_BASE + i;
        let link = connect(fleet.base_port + i as u16);
        send(&link, &gcs_heartbeat());
        let first = recv_until(&link, RECV_TIMEOUT, |header, message| match message {
            MavMessage::HEARTBEAT(_) if header.system_id == u32::from(system) => Some(()),
            _ => None,
        });
        assert!(first.is_some(), "no heartbeat from system {system}");

        let items = square(system, i as usize);
        upload(&link, system, &items);
        send(&link, &command(system, MavCmd::MAV_CMD_COMPONENT_ARM_DISARM, 1.0));
        send(&link, &command(system, MavCmd::MAV_CMD_MISSION_START, 0.0));

        let mut reached = vec![false; items.len()];
        recv_until(&link, REACHED_DEADLINE, |_, message| {
            if let MavMessage::MISSION_ITEM_REACHED(data) = message {
                if let Some(slot) = reached.get_mut(data.seq as usize) {
                    *slot = true;
                }
            }
            reached.iter().all(|done| *done).then_some(())
        });
        assert!(
            reached.iter().all(|done| *done),
            "system {system} reached only {reached:?}"
        );
    }
}

#[test]
fn a_count_of_zero_is_refused_with_a_message() {
    let output = Command::new(BIN)
        .args(["--count", "0"])
        .output()
        .expect("the binary runs");
    assert!(!output.status.success());
    assert_ne!(output.stderr.len(), 0);
}
