//! The `MAVLink` 2 wire format: one datagram in, its frames out.

const START_V2: u8 = 0xFD;
const START_V1: u8 = 0xFE;
const HEADER_V2: usize = 10;
const CRC_LEN: usize = 2;
const SIGNATURE_LEN: usize = 13;
const SIGNED_FLAG: u8 = 0x01;
const HEADER_V1: usize = 6;
const CRC_INIT: u16 = 0xFFFF;

const HEARTBEAT_ID: u32 = 0;
const SYS_STATUS_ID: u32 = 1;
const POSITION_ID: u32 = 33;

const HEARTBEAT_EXTRA: u8 = 50;
const SYS_STATUS_EXTRA: u8 = 124;
const POSITION_EXTRA: u8 = 104;

const HEARTBEAT_LEN: usize = 9;
const SYS_STATUS_LEN: usize = 31;
const POSITION_LEN: usize = 28;

/// One message of the subset the flight engine reads.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Message {
    /// HEARTBEAT (id 0).
    Heartbeat {
        /// The base mode flags.
        base_mode: u8,
        /// The system status.
        system_status: u8,
    },
    /// `SYS_STATUS` (id 1), reduced to the battery.
    SysStatus {
        /// The remaining battery in percent, or -1 when the Drone does not know it.
        battery_remaining: i8,
    },
    /// `GLOBAL_POSITION_INT` (id 33).
    GlobalPositionInt {
        /// Milliseconds since the Drone booted.
        time_boot_ms: u32,
        /// Latitude in degrees times 10^7.
        lat_e7: i32,
        /// Longitude in degrees times 10^7.
        lon_e7: i32,
        /// Altitude above mean sea level in millimetres.
        alt_mm: i32,
        /// Altitude above the home position in millimetres.
        relative_alt_mm: i32,
        /// Ground speed to the north in centimetres per second.
        vx_cm_s: i16,
        /// Ground speed to the east in centimetres per second.
        vy_cm_s: i16,
        /// Ground speed downwards in centimetres per second.
        vz_cm_s: i16,
        /// Heading in centidegrees.
        hdg_cdeg: u16,
    },
    /// Any other message, which is not unpacked.
    Other {
        /// The 24-bit message id.
        message_id: u32,
    },
}

/// One well-formed `MAVLink` 2 frame.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Frame {
    /// The sending system, which is the Drone.
    pub system_id: u8,
    /// The sending component.
    pub component_id: u8,
    /// The sequence number of the frame, which wraps from 255 to 0.
    pub sequence: u8,
    /// The decoded message.
    pub message: Message,
}

/// The result of decoding one datagram.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Decoded {
    /// The well-formed frames, in the order they sit in the datagram.
    pub frames: Vec<Frame>,
    /// How many frames were refused: bad CRC, truncated, `MAVLink` 1 or an unknown incompat flag.
    pub rejected: usize,
}

/// What one start byte led to.
enum Step {
    Frame(Frame, usize),
    Rejected(usize),
    Truncated,
}

/// Decode every `MAVLink` 2 frame of `datagram`.
///
/// Bytes before a start byte are skipped without being counted. A frame that is refused counts once in
/// `rejected`, and the scan goes on after it. It never panics, whatever the bytes.
#[must_use]
pub fn decode(datagram: &[u8]) -> Decoded {
    let mut frames = Vec::new();
    let rejected = scan(datagram, &mut |frame| frames.push(frame));
    Decoded { frames, rejected }
}

/// Call `on_frame` for each well-formed frame of `datagram` and return the number of rejected frames.
///
/// It does not allocate.
pub(crate) fn scan(datagram: &[u8], on_frame: &mut dyn FnMut(Frame)) -> usize {
    let mut rejected = 0;
    let mut position = 0;
    while let Some(rest) = datagram.get(position..) {
        let Some(start) = rest.first() else { break };
        let step = match *start {
            START_V2 => parse_v2(rest),
            START_V1 => parse_v1(rest),
            _ => {
                position += 1;
                continue;
            }
        };
        match step {
            Step::Frame(frame, used) => {
                on_frame(frame);
                position += used;
            }
            Step::Rejected(used) => {
                rejected += 1;
                position += used;
            }
            Step::Truncated => {
                rejected += 1;
                break;
            }
        }
    }
    rejected
}

fn parse_v1(rest: &[u8]) -> Step {
    let Some(length) = rest.get(1) else {
        return Step::Truncated;
    };
    let total = HEADER_V1 + usize::from(*length) + CRC_LEN;
    if rest.len() < total {
        return Step::Truncated;
    }
    Step::Rejected(total)
}

fn parse_v2(rest: &[u8]) -> Step {
    let Some(header) = rest.get(..HEADER_V2) else {
        return Step::Truncated;
    };
    let length = usize::from(header[1]);
    let incompat = header[2];
    let signature = if incompat & SIGNED_FLAG == 0 { 0 } else { SIGNATURE_LEN };
    let total = HEADER_V2 + length + CRC_LEN + signature;
    if rest.len() < total {
        return Step::Truncated;
    }
    if incompat & !SIGNED_FLAG != 0 {
        return Step::Rejected(total);
    }
    let message_id = u32::from_le_bytes([header[7], header[8], header[9], 0]);
    let (Some(payload), Some(wire_crc)) = (
        rest.get(HEADER_V2..HEADER_V2 + length),
        rest.get(HEADER_V2 + length..HEADER_V2 + length + CRC_LEN),
    ) else {
        return Step::Truncated;
    };
    if let Some(extra) = crc_extra(message_id) {
        let mut crc = crc_update(CRC_INIT, &header[1..]);
        crc = crc_update(crc, payload);
        crc = crc_update(crc, &[extra]);
        if crc.to_le_bytes() != [wire_crc[0], wire_crc[1]] {
            return Step::Rejected(total);
        }
    }
    let frame = Frame {
        system_id: header[5],
        component_id: header[6],
        sequence: header[4],
        message: unpack(message_id, payload),
    };
    Step::Frame(frame, total)
}

fn crc_extra(message_id: u32) -> Option<u8> {
    match message_id {
        HEARTBEAT_ID => Some(HEARTBEAT_EXTRA),
        SYS_STATUS_ID => Some(SYS_STATUS_EXTRA),
        POSITION_ID => Some(POSITION_EXTRA),
        _ => None,
    }
}

fn crc_update(start: u16, bytes: &[u8]) -> u16 {
    let mut crc = start;
    for byte in bytes {
        let mut tmp = *byte ^ crc.to_le_bytes()[0];
        tmp ^= tmp << 4;
        let wide = u16::from(tmp);
        crc = (crc >> 8) ^ (wide << 8) ^ (wide << 3) ^ (wide >> 4);
    }
    crc
}

fn unpack(message_id: u32, payload: &[u8]) -> Message {
    match message_id {
        HEARTBEAT_ID => {
            let fields = extend::<HEARTBEAT_LEN>(payload);
            Message::Heartbeat {
                base_mode: fields[6],
                system_status: fields[7],
            }
        }
        SYS_STATUS_ID => {
            let fields = extend::<SYS_STATUS_LEN>(payload);
            Message::SysStatus {
                battery_remaining: i8::from_le_bytes([fields[30]]),
            }
        }
        POSITION_ID => {
            let fields = extend::<POSITION_LEN>(payload);
            Message::GlobalPositionInt {
                time_boot_ms: u32::from_le_bytes(field(&fields, 0)),
                lat_e7: i32::from_le_bytes(field(&fields, 4)),
                lon_e7: i32::from_le_bytes(field(&fields, 8)),
                alt_mm: i32::from_le_bytes(field(&fields, 12)),
                relative_alt_mm: i32::from_le_bytes(field(&fields, 16)),
                vx_cm_s: i16::from_le_bytes(field(&fields, 20)),
                vy_cm_s: i16::from_le_bytes(field(&fields, 22)),
                vz_cm_s: i16::from_le_bytes(field(&fields, 24)),
                hdg_cdeg: u16::from_le_bytes(field(&fields, 26)),
            }
        }
        _ => Message::Other { message_id },
    }
}

/// Copy `payload` into `N` bytes: the missing tail is zero, the bytes past `N` are dropped.
fn extend<const N: usize>(payload: &[u8]) -> [u8; N] {
    let mut fields = [0_u8; N];
    let used = payload.len().min(N);
    if let (Some(target), Some(source)) = (fields.get_mut(..used), payload.get(..used)) {
        target.copy_from_slice(source);
    }
    fields
}

fn field<const N: usize>(fields: &[u8], at: usize) -> [u8; N] {
    let mut bytes = [0_u8; N];
    if let Some(source) = fields.get(at..at + N) {
        bytes.copy_from_slice(source);
    }
    bytes
}
