//! Integration tests of `swarm_core_mavlink::LatestFrames`, the latest frame per Drone.

mod common;

use common::{attitude, heartbeat, position, sys_status, Position};
use swarm_core_mavlink::LatestFrames;

#[test]
fn a_new_store_has_no_sample() {
    assert_eq!(LatestFrames::new().snapshot().len(), 0);
}

#[test]
fn ingest_returns_the_number_of_well_formed_frames() {
    let mut store = LatestFrames::new();
    let mut datagram = heartbeat(1, 4, 1, 3);
    datagram.extend(sys_status(2, 4, 50));
    assert_eq!(store.ingest(&datagram, 10), 2);
}

#[test]
fn the_latest_position_replaces_the_earlier_one() {
    let mut store = LatestFrames::new();
    let mut first = Position::sample();
    first.lat_e7 = 100;
    let mut second = Position::sample();
    second.lat_e7 = 200;
    second.relative_alt_mm = 999;
    store.ingest(&position(1, 4, first), 10);
    store.ingest(&position(2, 4, second), 20);
    let samples = store.snapshot();
    assert_eq!(samples.len(), 1);
    assert!(samples[0].has_position);
    assert_eq!(samples[0].lat_e7, 200);
    assert_eq!(samples[0].lon_e7, second.lon_e7);
    assert_eq!(samples[0].relative_alt_mm, 999);
    assert_eq!(samples[0].vx_cm_s, second.vx_cm_s);
    assert_eq!(samples[0].vy_cm_s, second.vy_cm_s);
    assert_eq!(samples[0].hdg_cdeg, second.hdg_cdeg);
}

#[test]
fn the_battery_is_minus_one_until_a_sys_status_arrives() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(1, 4, 1, 3), 10);
    assert_eq!(store.snapshot()[0].battery_remaining, -1);
    store.ingest(&sys_status(2, 4, 73), 20);
    assert_eq!(store.snapshot()[0].battery_remaining, 73);
}

#[test]
fn there_is_no_position_until_a_global_position_arrives() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(1, 4, 1, 3), 10);
    assert!(!store.snapshot()[0].has_position);
    store.ingest(&position(2, 4, Position::sample()), 20);
    assert!(store.snapshot()[0].has_position);
}

#[test]
fn the_system_status_is_zero_until_a_heartbeat_arrives() {
    let mut store = LatestFrames::new();
    store.ingest(&sys_status(1, 4, 50), 10);
    assert_eq!(store.snapshot()[0].system_status, 0);
    assert_eq!(store.snapshot()[0].base_mode, 0);
    store.ingest(&heartbeat(2, 4, 0x81, 4), 20);
    assert_eq!(store.snapshot()[0].system_status, 4);
    assert_eq!(store.snapshot()[0].base_mode, 0x81);
}

#[test]
fn a_sequence_gap_counts_the_lost_frames() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(10, 4, 1, 3), 10);
    store.ingest(&heartbeat(13, 4, 1, 3), 20);
    let samples = store.snapshot();
    assert_eq!(samples[0].received, 2);
    assert_eq!(samples[0].lost, 2);
}

#[test]
fn the_sequence_wraps_from_255_to_0_without_loss() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(255, 4, 1, 3), 10);
    store.ingest(&heartbeat(0, 4, 1, 3), 20);
    assert_eq!(store.snapshot()[0].lost, 0);
}

#[test]
fn the_sequence_is_followed_per_system() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(10, 4, 1, 3), 10);
    store.ingest(&heartbeat(50, 5, 1, 3), 20);
    store.ingest(&heartbeat(11, 4, 1, 3), 30);
    assert!(store.snapshot().iter().all(|sample| sample.lost == 0));
}

#[test]
fn other_frames_count_in_received_and_in_the_sequence() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(1, 4, 1, 3), 10);
    assert_eq!(store.ingest(&attitude(2, 4), 20), 1);
    store.ingest(&heartbeat(3, 4, 1, 3), 30);
    let samples = store.snapshot();
    assert_eq!(samples[0].received, 3);
    assert_eq!(samples[0].lost, 0);
}

#[test]
fn the_update_time_is_the_time_of_the_last_frame() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(1, 4, 1, 3), 1_000);
    store.ingest(&sys_status(2, 4, 50), 2_500);
    assert_eq!(store.snapshot()[0].updated_at_us, 2_500);
}

#[test]
fn a_rejected_frame_changes_nothing() {
    let mut store = LatestFrames::new();
    store.ingest(&heartbeat(1, 4, 1, 3), 10);
    let before = store.snapshot();
    let mut bad = heartbeat(5, 4, 1, 3);
    let last = bad.len() - 1;
    bad[last] ^= 0xFF;
    assert_eq!(store.ingest(&bad, 99), 0);
    assert_eq!(store.snapshot(), before);
}

#[test]
fn systems_are_listed_in_system_id_order() {
    let mut store = LatestFrames::new();
    for system in [9, 2, 200, 5] {
        store.ingest(&heartbeat(1, system, 1, 3), 10);
    }
    let ids: Vec<u8> = store.snapshot().iter().map(|sample| sample.system_id).collect();
    assert_eq!(ids, vec![2, 5, 9, 200]);
}
