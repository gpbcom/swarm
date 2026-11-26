//! Integration tests of `swarm_core_mavlink::decode`, the `MAVLink` 2 datagram decoder.

mod common;

use common::{
    attitude, frame, frame_with_flags, heartbeat, heartbeat_payload, position, position_payload, signed_frame,
    sys_status, Position, HEARTBEAT_EXTRA, POSITION_EXTRA,
};
use swarm_core_mavlink::{decode, Message};

#[test]
fn a_heartbeat_decodes_to_its_fields() {
    let decoded = decode(&heartbeat(7, 3, 0x81, 4));
    assert_eq!(decoded.rejected, 0);
    assert_eq!(decoded.frames.len(), 1);
    let frame = &decoded.frames[0];
    assert_eq!((frame.system_id, frame.component_id, frame.sequence), (3, 1, 7));
    assert_eq!(
        frame.message,
        Message::Heartbeat {
            base_mode: 0x81,
            system_status: 4
        }
    );
}

#[test]
fn a_sys_status_decodes_its_battery() {
    let decoded = decode(&sys_status(1, 2, 87));
    assert_eq!(decoded.frames[0].message, Message::SysStatus { battery_remaining: 87 });
}

#[test]
fn a_negative_battery_decodes_as_unknown() {
    let decoded = decode(&sys_status(1, 2, -1));
    assert_eq!(decoded.frames[0].message, Message::SysStatus { battery_remaining: -1 });
}

#[test]
fn a_global_position_decodes_to_its_fields() {
    let decoded = decode(&position(9, 5, Position::sample()));
    assert_eq!(decoded.rejected, 0);
    assert_eq!(
        decoded.frames[0].message,
        Message::GlobalPositionInt {
            time_boot_ms: 123_456,
            lat_e7: 473_977_420,
            lon_e7: -85_455_940,
            alt_mm: 510_000,
            relative_alt_mm: 12_500,
            vx_cm_s: 150,
            vy_cm_s: -75,
            vz_cm_s: 10,
            hdg_cdeg: 27_000,
        }
    );
}

#[test]
fn a_trimmed_payload_is_extended_with_zeros() {
    let mut fields = Position::sample();
    fields.vz_cm_s = 0;
    fields.hdg_cdeg = 0;
    let datagram = position(1, 1, fields);
    assert!(datagram.len() < 12 + position_payload(fields).len());
    let decoded = decode(&datagram);
    assert_eq!(decoded.rejected, 0);
    assert_eq!(
        decoded.frames[0].message,
        Message::GlobalPositionInt {
            time_boot_ms: 123_456,
            lat_e7: 473_977_420,
            lon_e7: -85_455_940,
            alt_mm: 510_000,
            relative_alt_mm: 12_500,
            vx_cm_s: 150,
            vy_cm_s: -75,
            vz_cm_s: 0,
            hdg_cdeg: 0,
        }
    );
}

#[test]
fn two_frames_in_one_datagram_decode_in_order() {
    let mut datagram = heartbeat(1, 4, 1, 3);
    datagram.extend(sys_status(2, 4, 60));
    let decoded = decode(&datagram);
    assert_eq!(decoded.rejected, 0);
    assert_eq!(decoded.frames.len(), 2);
    assert_eq!(decoded.frames[0].sequence, 1);
    assert_eq!(decoded.frames[1].message, Message::SysStatus { battery_remaining: 60 });
}

#[test]
fn garbage_before_the_start_byte_is_skipped() {
    let mut datagram = vec![0x00, 0x11, 0x22];
    datagram.extend(heartbeat(1, 4, 1, 3));
    let decoded = decode(&datagram);
    assert_eq!(decoded.frames.len(), 1);
}

#[test]
fn a_signed_frame_decodes_and_its_signature_is_skipped() {
    let mut datagram = signed_frame(1, 6, 0, HEARTBEAT_EXTRA, &heartbeat_payload(1, 3));
    datagram.extend(heartbeat(2, 6, 1, 4));
    let decoded = decode(&datagram);
    assert_eq!(decoded.rejected, 0);
    assert_eq!(decoded.frames.len(), 2);
    assert_eq!(decoded.frames[1].sequence, 2);
}

#[test]
fn a_bad_crc_is_rejected() {
    let mut datagram = heartbeat(1, 4, 1, 3);
    let last = datagram.len() - 1;
    datagram[last] ^= 0xFF;
    let decoded = decode(&datagram);
    assert_eq!(decoded.frames.len(), 0);
    assert_eq!(decoded.rejected, 1);
}

#[test]
fn a_truncated_frame_is_rejected() {
    let mut datagram = heartbeat(1, 4, 1, 3);
    datagram.truncate(datagram.len() - 4);
    let decoded = decode(&datagram);
    assert_eq!(decoded.frames.len(), 0);
    assert_eq!(decoded.rejected, 1);
}

#[test]
fn a_mavlink_1_frame_is_rejected() {
    let decoded = decode(&[0xFE, 9, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]);
    assert_eq!(decoded.frames.len(), 0);
    assert_eq!(decoded.rejected, 1);
}

#[test]
fn an_unknown_incompat_flag_is_rejected() {
    let datagram = frame_with_flags(0x02, 1, 4, 0, HEARTBEAT_EXTRA, &heartbeat_payload(1, 3));
    let decoded = decode(&datagram);
    assert_eq!(decoded.frames.len(), 0);
    assert_eq!(decoded.rejected, 1);
}

#[test]
fn an_unknown_message_id_decodes_to_other() {
    let decoded = decode(&attitude(1, 4));
    assert_eq!(decoded.rejected, 0);
    assert_eq!(decoded.frames[0].message, Message::Other { message_id: 30 });
}

#[test]
fn an_empty_datagram_gives_nothing() {
    let decoded = decode(&[]);
    assert_eq!(decoded.frames.len(), 0);
    assert_eq!(decoded.rejected, 0);
}

#[test]
fn a_frame_with_a_wrong_extra_byte_is_rejected() {
    let datagram = frame(1, 4, 33, POSITION_EXTRA ^ 0x55, &position_payload(Position::sample()));
    let decoded = decode(&datagram);
    assert_eq!(decoded.frames.len(), 0);
    assert_eq!(decoded.rejected, 1);
}

#[test]
fn fixed_arbitrary_bytes_never_panic() {
    let samples: [&[u8]; 8] = [
        &[0xFD],
        &[0xFD, 0xFF],
        &[0xFD, 0xFF, 0, 0, 0, 0, 0, 0, 0, 0],
        &[0xFD, 0, 1, 0, 0, 0, 0, 0xFF, 0xFF, 0xFF],
        &[0xFD, 0xFD, 0xFD, 0xFD, 0xFD, 0xFD],
        &[0xFF; 300],
        &[0x00; 64],
        &[0xFD, 28, 0, 0, 1, 1, 1, 33, 0, 0, 1, 2, 3],
    ];
    for sample in samples {
        let decoded = decode(sample);
        assert!(decoded.frames.len() <= sample.len());
    }
}
