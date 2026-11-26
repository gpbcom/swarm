//! The latest frame of each Drone, kept so that a slow Drone never makes the flight engine wait.

use crate::frame::{scan, Frame, Message};

/// How many system ids exist: the system id is one byte.
const SYSTEMS: usize = 256;

/// What the flight engine knows of one Drone, from its latest frames.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct DroneSample {
    /// The system id of the Drone.
    pub system_id: u8,
    /// True once a `GLOBAL_POSITION_INT` has arrived.
    pub has_position: bool,
    /// Latitude in degrees times 10^7, from the latest position.
    pub lat_e7: i32,
    /// Longitude in degrees times 10^7, from the latest position.
    pub lon_e7: i32,
    /// Altitude above the home position in millimetres, from the latest position.
    pub relative_alt_mm: i32,
    /// Ground speed to the north in centimetres per second, from the latest position.
    pub vx_cm_s: i16,
    /// Ground speed to the east in centimetres per second, from the latest position.
    pub vy_cm_s: i16,
    /// Heading in centidegrees, from the latest position.
    pub hdg_cdeg: u16,
    /// The remaining battery in percent, or -1 until a `SYS_STATUS` arrives.
    pub battery_remaining: i8,
    /// The base mode of the latest HEARTBEAT, 0 until one arrives.
    pub base_mode: u8,
    /// The system status of the latest HEARTBEAT, 0 until one arrives.
    pub system_status: u8,
    /// The number of frames received from this Drone, of any message.
    pub received: u64,
    /// The number of frames lost, counted from the gaps in the sequence numbers.
    pub lost: u64,
    /// The `now_us` given with the latest frame.
    pub updated_at_us: u64,
}

impl DroneSample {
    fn new(system_id: u8) -> Self {
        Self {
            system_id,
            has_position: false,
            lat_e7: 0,
            lon_e7: 0,
            relative_alt_mm: 0,
            vx_cm_s: 0,
            vy_cm_s: 0,
            hdg_cdeg: 0,
            battery_remaining: -1,
            base_mode: 0,
            system_status: 0,
            received: 0,
            lost: 0,
            updated_at_us: 0,
        }
    }
}

/// A Drone's sample and the sequence number of its latest frame.
#[derive(Clone, Copy)]
struct Entry {
    sample: DroneSample,
    last_sequence: u8,
}

/// The latest frame of each Drone, indexed by system id.
///
/// `ingest` does not allocate once the store exists.
pub struct LatestFrames {
    entries: Vec<Option<Entry>>,
}

impl Default for LatestFrames {
    fn default() -> Self {
        Self::new()
    }
}

impl LatestFrames {
    /// Create an empty store.
    #[must_use]
    pub fn new() -> Self {
        Self {
            entries: vec![None; SYSTEMS],
        }
    }

    /// Take the well-formed frames of `datagram`, received at `now_us`, and return how many there were.
    ///
    /// A rejected frame changes nothing. The sequence gaps of each system add to its `lost`, and the
    /// sequence wraps from 255 to 0.
    pub fn ingest(&mut self, datagram: &[u8], now_us: u64) -> usize {
        let mut taken = 0;
        let entries = &mut self.entries;
        scan(datagram, &mut |frame| {
            taken += 1;
            apply(entries, &frame, now_us);
        });
        taken
    }

    /// Return the sample of every Drone heard from, ordered by system id.
    #[must_use]
    pub fn snapshot(&self) -> Vec<DroneSample> {
        self.entries.iter().flatten().map(|entry| entry.sample).collect()
    }
}

fn apply(entries: &mut [Option<Entry>], frame: &Frame, now_us: u64) {
    let Some(slot) = entries.get_mut(usize::from(frame.system_id)) else {
        return;
    };
    let entry = slot.get_or_insert_with(|| Entry {
        sample: DroneSample::new(frame.system_id),
        last_sequence: frame.sequence,
    });
    let sample = &mut entry.sample;
    if sample.received > 0 {
        let gap = frame.sequence.wrapping_sub(entry.last_sequence).wrapping_sub(1);
        sample.lost = sample.lost.saturating_add(u64::from(gap));
    }
    entry.last_sequence = frame.sequence;
    sample.received = sample.received.saturating_add(1);
    sample.updated_at_us = now_us;
    match frame.message {
        Message::Heartbeat {
            base_mode,
            system_status,
        } => {
            sample.base_mode = base_mode;
            sample.system_status = system_status;
        }
        Message::SysStatus { battery_remaining } => sample.battery_remaining = battery_remaining,
        Message::GlobalPositionInt {
            lat_e7,
            lon_e7,
            relative_alt_mm,
            vx_cm_s,
            vy_cm_s,
            hdg_cdeg,
            ..
        } => {
            sample.has_position = true;
            sample.lat_e7 = lat_e7;
            sample.lon_e7 = lon_e7;
            sample.relative_alt_mm = relative_alt_mm;
            sample.vx_cm_s = vx_cm_s;
            sample.vy_cm_s = vy_cm_s;
            sample.hdg_cdeg = hdg_cdeg;
        }
        Message::Other { .. } => {}
    }
}
