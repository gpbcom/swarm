//! Test that a closed collector never stops the synthetic Drones from flying.
#![allow(deprecated)]
#![allow(clippy::cast_possible_truncation)]

use std::net::UdpSocket;
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

use mavlink::dialects::common::{MavAutopilot, MavMessage, MavModeFlag, MavState, MavType, HEARTBEAT_DATA};
use mavlink::{MAVLinkV2MessageRaw, MavHeader};

const BIN: &str = env!("CARGO_BIN_EXE_swarm-synthetic-drones");
const ENDPOINT_VARIABLE: &str = "OTEL_EXPORTER_OTLP_ENDPOINT";
const RECEIVE_DEADLINE: Duration = Duration::from_secs(20);
const MAVLINK_MAGIC_V2: u8 = 0xFD;

struct Fleet {
    child: Child,
}

impl Drop for Fleet {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn gcs_heartbeat_frame() -> MAVLinkV2MessageRaw {
    let header = MavHeader {
        system_id: 255,
        component_id: 190,
        sequence: 0,
    };
    let message = MavMessage::HEARTBEAT(HEARTBEAT_DATA {
        custom_mode: 0,
        mavtype: MavType::MAV_TYPE_GCS,
        autopilot: MavAutopilot::MAV_AUTOPILOT_INVALID,
        base_mode: MavModeFlag::empty(),
        system_status: MavState::MAV_STATE_ACTIVE,
        mavlink_version: 3,
    });
    let mut raw = MAVLinkV2MessageRaw::new();
    raw.serialize_message(header, &message);
    raw
}

fn closed_tcp_port() -> u16 {
    let listener = std::net::TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.local_addr().expect("address").port()
}

fn free_udp_port() -> u16 {
    for attempt in 0..50u16 {
        let port = 34_000 + (std::process::id() as u16 % 2_000) + attempt * 7;
        if UdpSocket::bind(("127.0.0.1", port)).is_ok() {
            return port;
        }
    }
    panic!("no free UDP port");
}

#[test]
fn a_closed_collector_does_not_stop_the_drones_from_sending_mavlink() {
    let collector = closed_tcp_port();
    let port = free_udp_port();
    let child = Command::new(BIN)
        .args(["--count", "1"])
        .args(["--base-port", &port.to_string()])
        .args(["--tick-ms", "20"])
        .env(ENDPOINT_VARIABLE, format!("http://127.0.0.1:{collector}"))
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .expect("the binary starts");
    let _fleet = Fleet { child };

    let socket = UdpSocket::bind("127.0.0.1:0").expect("bind");
    socket
        .set_read_timeout(Some(Duration::from_millis(500)))
        .expect("timeout");
    let end = Instant::now() + RECEIVE_DEADLINE;
    let mut buffer = [0u8; 512];
    let mut heard = false;
    let frame = gcs_heartbeat_frame();
    while Instant::now() < end && !heard {
        let _ = socket.send_to(frame.raw_bytes(), ("127.0.0.1", port));
        if let Ok((length, _)) = socket.recv_from(&mut buffer) {
            heard = length > 0 && buffer[0] == MAVLINK_MAGIC_V2;
        }
    }
    assert!(heard, "no MAVLink datagram arrived");
}
