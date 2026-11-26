//! Independent `MAVLink` 2 frame builders shared by the decoder tests.

#![allow(dead_code, missing_docs)]

/// `CRC_EXTRA` of HEARTBEAT.
pub const HEARTBEAT_EXTRA: u8 = 50;
/// `CRC_EXTRA` of `SYS_STATUS`.
pub const SYS_STATUS_EXTRA: u8 = 124;
/// `CRC_EXTRA` of `GLOBAL_POSITION_INT`.
pub const POSITION_EXTRA: u8 = 104;
/// Message id of ATTITUDE, a message the decoder does not unpack.
pub const ATTITUDE_ID: u32 = 30;
/// `CRC_EXTRA` of ATTITUDE.
pub const ATTITUDE_EXTRA: u8 = 39;

/// The fields of a `GLOBAL_POSITION_INT` message.
#[derive(Clone, Copy)]
pub struct Position {
    pub time_boot_ms: u32,
    pub lat_e7: i32,
    pub lon_e7: i32,
    pub alt_mm: i32,
    pub relative_alt_mm: i32,
    pub vx_cm_s: i16,
    pub vy_cm_s: i16,
    pub vz_cm_s: i16,
    pub hdg_cdeg: u16,
}

impl Position {
    /// A position with every field set to a distinct non-zero value.
    pub fn sample() -> Self {
        Self {
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
    }
}

/// CRC-16/MCRF4XX (X.25) of `bytes`, starting from 0xFFFF.
pub fn crc16(bytes: &[u8]) -> u16 {
    let mut crc: u16 = 0xFFFF;
    for byte in bytes {
        let mut tmp = *byte ^ crc.to_le_bytes()[0];
        tmp ^= tmp << 4;
        let tmp16 = u16::from(tmp);
        crc = (crc >> 8) ^ (tmp16 << 8) ^ (tmp16 << 3) ^ (tmp16 >> 4);
    }
    crc
}

/// Remove the trailing zero bytes of `payload`, keeping at least one byte.
pub fn trim(payload: &[u8]) -> Vec<u8> {
    let mut end = payload.len();
    while end > 1 && payload[end - 1] == 0 {
        end -= 1;
    }
    payload[..end].to_vec()
}

/// Build one `MAVLink` 2 frame around `payload`, sent as given, with a valid CRC.
pub fn frame_with_flags(
    incompat_flags: u8,
    sequence: u8,
    system_id: u8,
    message_id: u32,
    extra: u8,
    payload: &[u8],
) -> Vec<u8> {
    let mut bytes = vec![
        0xFD,
        u8::try_from(payload.len()).expect("payload fits one byte"),
        incompat_flags,
        0,
        sequence,
        system_id,
        1,
    ];
    bytes.extend_from_slice(&message_id.to_le_bytes()[..3]);
    bytes.extend_from_slice(payload);
    let mut covered = bytes[1..].to_vec();
    covered.push(extra);
    bytes.extend_from_slice(&crc16(&covered).to_le_bytes());
    bytes
}

/// Build one unsigned frame around `payload`.
pub fn frame(sequence: u8, system_id: u8, message_id: u32, extra: u8, payload: &[u8]) -> Vec<u8> {
    frame_with_flags(0, sequence, system_id, message_id, extra, payload)
}

/// Build one signed frame: flag 0x01 and a 13-byte signature after the CRC.
pub fn signed_frame(sequence: u8, system_id: u8, message_id: u32, extra: u8, payload: &[u8]) -> Vec<u8> {
    let mut bytes = frame_with_flags(1, sequence, system_id, message_id, extra, payload);
    bytes.extend_from_slice(&[0xAB; 13]);
    bytes
}

/// The 9-byte HEARTBEAT payload.
pub fn heartbeat_payload(base_mode: u8, system_status: u8) -> Vec<u8> {
    let mut payload = 0_u32.to_le_bytes().to_vec();
    payload.extend_from_slice(&[2, 3, base_mode, system_status, 3]);
    payload
}

/// The 31-byte `SYS_STATUS` payload, with the battery at offset 30.
pub fn sys_status_payload(battery_remaining: i8) -> Vec<u8> {
    let mut payload = vec![0_u8; 30];
    payload.extend_from_slice(&battery_remaining.to_le_bytes());
    payload
}

/// The 28-byte `GLOBAL_POSITION_INT` payload.
pub fn position_payload(position: Position) -> Vec<u8> {
    let mut payload = position.time_boot_ms.to_le_bytes().to_vec();
    payload.extend_from_slice(&position.lat_e7.to_le_bytes());
    payload.extend_from_slice(&position.lon_e7.to_le_bytes());
    payload.extend_from_slice(&position.alt_mm.to_le_bytes());
    payload.extend_from_slice(&position.relative_alt_mm.to_le_bytes());
    payload.extend_from_slice(&position.vx_cm_s.to_le_bytes());
    payload.extend_from_slice(&position.vy_cm_s.to_le_bytes());
    payload.extend_from_slice(&position.vz_cm_s.to_le_bytes());
    payload.extend_from_slice(&position.hdg_cdeg.to_le_bytes());
    payload
}

/// A full-length HEARTBEAT frame.
pub fn heartbeat(sequence: u8, system_id: u8, base_mode: u8, system_status: u8) -> Vec<u8> {
    frame(
        sequence,
        system_id,
        0,
        HEARTBEAT_EXTRA,
        &heartbeat_payload(base_mode, system_status),
    )
}

/// A `SYS_STATUS` frame, trimmed like a real sender does.
pub fn sys_status(sequence: u8, system_id: u8, battery_remaining: i8) -> Vec<u8> {
    frame(
        sequence,
        system_id,
        1,
        SYS_STATUS_EXTRA,
        &trim(&sys_status_payload(battery_remaining)),
    )
}

/// A `GLOBAL_POSITION_INT` frame, trimmed like a real sender does.
pub fn position(sequence: u8, system_id: u8, position: Position) -> Vec<u8> {
    frame(
        sequence,
        system_id,
        33,
        POSITION_EXTRA,
        &trim(&position_payload(position)),
    )
}

/// An ATTITUDE frame (message id 30), a message the decoder reports as `Other`.
pub fn attitude(sequence: u8, system_id: u8) -> Vec<u8> {
    let payload: Vec<u8> = (1..=28).collect();
    frame(sequence, system_id, ATTITUDE_ID, ATTITUDE_EXTRA, &payload)
}
