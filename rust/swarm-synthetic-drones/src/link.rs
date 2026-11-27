//! The UDP runtime of the synthetic Drones: a [`Fleet`] of Drones, each on its own socket.
//!
//! A [`Fleet`] binds one non-blocking UDP socket per Drone, on consecutive ports, and runs all of them on one
//! thread. On each tick it reads every pending datagram of each socket, parses it as `MAVLink` 2 and hands the
//! messages to the [`SyntheticDrone`] of that socket. A Drone answers only the last peer it received a valid message
//! from, and sends its position every tick and its `HEARTBEAT` once per second to that peer.
//!
//! The buffers are reused between ticks: a tick allocates nothing once the output vector has grown to the most
//! messages a Drone emits in one tick.

// The messages of the Drone carry the deprecated mission frames on purpose, as the drone module does.
#![allow(deprecated)]

use std::error::Error;
use std::fmt;
use std::io;
use std::net::{IpAddr, Ipv4Addr, SocketAddr, UdpSocket};
use std::thread;
use std::time::{Duration, Instant};

use mavlink::dialects::common::{MavComponent, MavMessage};
use mavlink::{MAVLinkV2MessageRaw, MavHeader, MavlinkReader, MavlinkVersion};

use crate::drone::{DroneConfig, SyntheticDrone};
use crate::route::{offset, Position};

/// The most Drones a fleet may hold, so that each has its own `MAVLink` system id.
pub const MAX_COUNT: u8 = 255;

/// The default number of Drones.
pub const DEFAULT_COUNT: u8 = 10;

/// The default UDP port of the first Drone.
pub const DEFAULT_BASE_PORT: u16 = 14_600;

/// The default latitude of the first Drone's home, in degrees times ten million.
pub const DEFAULT_HOME_LAT_E7: i32 = 473_977_420;

/// The default longitude of the first Drone's home, in degrees times ten million.
pub const DEFAULT_HOME_LON_E7: i32 = 85_455_940;

/// The default distance, in metres, between the homes of two neighbouring Drones.
pub const DEFAULT_SPACING_M: f32 = 5.0;

/// The default speed, in metres per second, of every flight.
pub const DEFAULT_SPEED_M_S: f32 = 10.0;

/// The default duration of a tick, in milliseconds.
pub const DEFAULT_TICK_MS: u32 = 50;

/// The period, in seconds, of the `HEARTBEAT` of a Drone.
const HEARTBEAT_PERIOD_S: f32 = 1.0;

/// The largest latitude, in degrees times ten million, of a home: the east axis of the projection stretches without
/// bound near the poles.
const HOME_LAT_E7_MAX: i32 = 890_000_000;

/// The largest longitude, in degrees times ten million, of a home.
const HOME_LON_E7_MAX: i32 = 1_800_000_000;

/// The size of the buffer a datagram is read into, above the 280 bytes of the largest `MAVLink` 2 frame.
const DATAGRAM_BYTES: usize = 512;

/// The most datagrams read from one socket in one tick, so that a flooding peer cannot starve the other Drones.
const MAX_DATAGRAMS_PER_TICK: usize = 64;

/// The longest step, in ticks, that a late tick may simulate, so that a stalled process does not make Drones jump.
const MAX_CATCH_UP_TICKS: u32 = 5;

/// What a fleet is built from.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct FleetConfig {
    /// The number of Drones, from 1 to [`MAX_COUNT`].
    pub count: u8,
    /// The address the sockets are bound to.
    pub bind: IpAddr,
    /// The UDP port of the first Drone: Drone `i` listens on `base_port + i`.
    pub base_port: u16,
    /// The `MAVLink` system id of the first Drone: Drone `i` answers to `system_id_base + i`.
    pub system_id_base: u8,
    /// The latitude of the first home, in degrees times ten million.
    pub home_lat_e7: i32,
    /// The longitude of the first home, in degrees times ten million.
    pub home_lon_e7: i32,
    /// The distance in metres, towards the east, between two neighbouring homes.
    pub spacing_m: f32,
    /// The constant speed, in metres per second, of every flight.
    pub speed_m_s: f32,
    /// The duration of a tick, in milliseconds.
    pub tick_ms: u32,
}

impl Default for FleetConfig {
    fn default() -> Self {
        Self {
            count: DEFAULT_COUNT,
            bind: IpAddr::V4(Ipv4Addr::LOCALHOST),
            base_port: DEFAULT_BASE_PORT,
            system_id_base: 1,
            home_lat_e7: DEFAULT_HOME_LAT_E7,
            home_lon_e7: DEFAULT_HOME_LON_E7,
            spacing_m: DEFAULT_SPACING_M,
            speed_m_s: DEFAULT_SPEED_M_S,
            tick_ms: DEFAULT_TICK_MS,
        }
    }
}

impl FleetConfig {
    /// Checks that the configuration describes a fleet that can run.
    ///
    /// # Errors
    ///
    /// [`FleetError::Invalid`] names the first field that is out of range.
    pub fn validate(&self) -> Result<(), FleetError> {
        if self.count == 0 {
            return Err(FleetError::invalid("count", "must be from 1 to 255"));
        }
        let last = u32::from(self.count) - 1;
        if self.system_id_base == 0 || u32::from(self.system_id_base) + last > u32::from(MAX_COUNT) {
            return Err(FleetError::invalid(
                "system-id-base",
                "must leave a system id from 1 to 255 for every Drone",
            ));
        }
        if self.base_port == 0 || u32::from(self.base_port) + last > u32::from(u16::MAX) {
            return Err(FleetError::invalid(
                "base-port",
                "must leave a port from 1 to 65535 for every Drone",
            ));
        }
        if self.home_lat_e7.abs() > HOME_LAT_E7_MAX {
            return Err(FleetError::invalid(
                "home-lat-e7",
                "must be within 89 degrees of the equator",
            ));
        }
        if self.home_lon_e7.abs() > HOME_LON_E7_MAX {
            return Err(FleetError::invalid(
                "home-lon-e7",
                "must be within 180 degrees of the meridian",
            ));
        }
        if !self.spacing_m.is_finite() || self.spacing_m < 0.0 {
            return Err(FleetError::invalid(
                "spacing-m",
                "must be a number of metres, zero or more",
            ));
        }
        if !self.speed_m_s.is_finite() || self.speed_m_s <= 0.0 {
            return Err(FleetError::invalid(
                "speed-m-s",
                "must be a number of metres per second above zero",
            ));
        }
        if self.tick_ms == 0 {
            return Err(FleetError::invalid("tick-ms", "must be at least 1"));
        }
        Ok(())
    }
}

/// Why a fleet could not be built.
#[derive(Debug)]
pub enum FleetError {
    /// A field of the configuration is out of range.
    Invalid {
        /// The name of the field, as the command line spells it.
        field: &'static str,
        /// What the field must be.
        reason: &'static str,
    },
    /// A socket could not be bound or configured.
    Io {
        /// The address that was being bound.
        address: SocketAddr,
        /// The error of the operating system.
        source: io::Error,
    },
}

impl FleetError {
    /// A [`FleetError::Invalid`] for `field`.
    fn invalid(field: &'static str, reason: &'static str) -> Self {
        Self::Invalid { field, reason }
    }
}

impl fmt::Display for FleetError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Invalid { field, reason } => write!(formatter, "invalid --{field}: it {reason}"),
            Self::Io { address, source } => write!(formatter, "cannot bind {address}: {source}"),
        }
    }
}

impl Error for FleetError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            Self::Invalid { .. } => None,
            Self::Io { source, .. } => Some(source),
        }
    }
}

/// The buffers every Drone of a fleet shares, reused from tick to tick.
struct Scratch {
    datagram: [u8; DATAGRAM_BYTES],
    out: Vec<MavMessage>,
    frame: MAVLinkV2MessageRaw,
    /// The frames the system accepted since [`Fleet::take_frames_sent`] last emptied it.
    frames_sent: u64,
}

/// One Drone with its socket, the peer it answers and its `MAVLink` sequence number.
struct Slot {
    socket: UdpSocket,
    drone: SyntheticDrone,
    peer: Option<SocketAddr>,
    sequence: u8,
}

impl Slot {
    /// Reads the pending datagrams, hands their messages to the Drone and sends its answers after each one.
    fn receive(&mut self, scratch: &mut Scratch) {
        for _ in 0..MAX_DATAGRAMS_PER_TICK {
            match self.socket.recv_from(&mut scratch.datagram) {
                Ok((length, from)) => {
                    let length = length.min(DATAGRAM_BYTES);
                    let mut reader = MavlinkReader::new(&scratch.datagram[..length]);
                    let mut understood = false;
                    while let Ok((_, message)) = reader.read_message::<MavMessage>(MavlinkVersion::V2) {
                        understood = true;
                        self.drone.handle(&message, &mut scratch.out);
                    }
                    if understood {
                        self.peer = Some(from);
                    }
                    self.flush(scratch);
                }
                Err(error) if error.kind() == io::ErrorKind::Interrupted => {}
                Err(_) => break,
            }
        }
    }

    /// Moves the Drone and sends its position, the item it reached and, when `beat` is set, its `HEARTBEAT`.
    fn tick(&mut self, dt_s: f32, beat: bool, scratch: &mut Scratch) {
        if beat {
            scratch.out.push(self.drone.heartbeat());
        }
        self.drone.tick(dt_s, &mut scratch.out);
        self.flush(scratch);
    }

    /// Sends the messages of `scratch.out` to the peer, if there is one, then empties it.
    ///
    /// The send is best effort, as UDP is: a datagram the system refuses is dropped.
    fn flush(&mut self, scratch: &mut Scratch) {
        if let Some(peer) = self.peer {
            for message in &scratch.out {
                let header = MavHeader {
                    system_id: u32::from(self.drone.system_id()),
                    component_id: MavComponent::MAV_COMP_ID_AUTOPILOT1 as u8,
                    sequence: self.sequence,
                };
                self.sequence = self.sequence.wrapping_add(1);
                scratch.frame.serialize_message(header, message);
                if self.socket.send_to(scratch.frame.raw_bytes(), peer).is_ok() {
                    scratch.frames_sent += 1;
                }
            }
        }
        scratch.out.clear();
    }
}

/// Synthetic Drones, each listening on its own UDP socket, run by one thread.
pub struct Fleet {
    slots: Vec<Slot>,
    scratch: Scratch,
    tick: Duration,
    since_heartbeat_s: f32,
}

impl Fleet {
    /// Binds one socket per Drone and builds the Drones, landed and disarmed at their homes.
    ///
    /// Drone `i` listens on `bind:base_port + i`, answers to the system id `system_id_base + i` and stands
    /// `i * spacing_m` metres east of the first home.
    ///
    /// # Errors
    ///
    /// [`FleetError::Invalid`] when the configuration is out of range, and [`FleetError::Io`] when a socket cannot
    /// be bound.
    pub fn new(config: &FleetConfig) -> Result<Self, FleetError> {
        config.validate()?;
        let home = Position {
            lat_e7: config.home_lat_e7,
            lon_e7: config.home_lon_e7,
            altitude_m: 0.0,
        };
        let mut slots = Vec::with_capacity(usize::from(config.count));
        for index in 0..config.count {
            let address = SocketAddr::new(config.bind, config.base_port + u16::from(index));
            let io_error = |source| FleetError::Io { address, source };
            let socket = UdpSocket::bind(address).map_err(io_error)?;
            socket.set_nonblocking(true).map_err(io_error)?;
            let drone = SyntheticDrone::new(DroneConfig {
                system_id: config.system_id_base + index,
                home: offset(home, 0.0, config.spacing_m * f32::from(index)),
                speed_m_s: config.speed_m_s,
            });
            slots.push(Slot {
                socket,
                drone,
                peer: None,
                sequence: 0,
            });
        }
        Ok(Self {
            slots,
            scratch: Scratch {
                datagram: [0; DATAGRAM_BYTES],
                out: Vec::with_capacity(8),
                frame: MAVLinkV2MessageRaw::default(),
                frames_sent: 0,
            },
            tick: Duration::from_millis(u64::from(config.tick_ms)),
            since_heartbeat_s: HEARTBEAT_PERIOD_S,
        })
    }

    /// The address the socket of Drone `index` is bound to, or `None` when the fleet has no such Drone.
    #[must_use]
    pub fn local_addr(&self, index: usize) -> Option<SocketAddr> {
        self.slots.get(index)?.socket.local_addr().ok()
    }

    /// The number of Drones.
    #[must_use]
    pub fn count(&self) -> usize {
        self.slots.len()
    }

    /// Runs one tick of `dt_s` seconds: every Drone reads what its socket holds, moves, and sends what it emits.
    ///
    /// The `HEARTBEAT` is sent on the first tick and then once per second of simulated time.
    pub fn step(&mut self, dt_s: f32) {
        self.since_heartbeat_s += dt_s;
        let beat = self.since_heartbeat_s >= HEARTBEAT_PERIOD_S;
        if beat {
            self.since_heartbeat_s = 0.0;
        }
        for slot in &mut self.slots {
            slot.receive(&mut self.scratch);
            slot.tick(dt_s, beat, &mut self.scratch);
        }
    }

    /// The number of `MAVLink` frames the system accepted since the last call, and empties the count.
    ///
    /// The count is a plain integer kept by the send loop, so that observing it costs nothing per frame.
    pub fn take_frames_sent(&mut self) -> u64 {
        std::mem::take(&mut self.scratch.frames_sent)
    }

    /// Runs a tick every `tick_ms` for ever, on the calling thread.
    ///
    /// A tick that starts late simulates the time that really went by, up to five ticks.
    pub fn run(&mut self) -> ! {
        loop {
            self.run_until(|_| true);
        }
    }

    /// Runs a tick every `tick_ms` on the calling thread, and calls `after_tick` with the fleet after each one.
    ///
    /// It returns when `after_tick` returns `false`. A tick that starts late simulates the time that really went
    /// by, up to five ticks.
    pub fn run_until(&mut self, mut after_tick: impl FnMut(&mut Self) -> bool) {
        let mut last = Instant::now();
        let mut next = last + self.tick;
        loop {
            if let Some(wait) = next.checked_duration_since(Instant::now()) {
                thread::sleep(wait);
            }
            let now = Instant::now();
            let elapsed = now.duration_since(last).min(self.tick * MAX_CATCH_UP_TICKS);
            last = now;
            self.step(elapsed.as_secs_f32());
            if !after_tick(self) {
                return;
            }
            next += self.tick;
            if next < now {
                next = now + self.tick;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_default_configuration_is_valid() {
        assert!(FleetConfig::default().validate().is_ok());
    }

    #[test]
    fn a_count_of_zero_is_refused() {
        let config = FleetConfig {
            count: 0,
            ..FleetConfig::default()
        };
        assert!(matches!(
            config.validate(),
            Err(FleetError::Invalid { field: "count", .. })
        ));
    }

    #[test]
    fn system_ids_and_ports_must_fit_for_every_drone() {
        let ids = FleetConfig {
            count: 10,
            system_id_base: 250,
            ..FleetConfig::default()
        };
        assert!(ids.validate().is_err());
        let ports = FleetConfig {
            count: 10,
            base_port: 65_530,
            ..FleetConfig::default()
        };
        assert!(ports.validate().is_err());
    }

    #[test]
    fn a_speed_that_is_not_positive_is_refused() {
        for speed_m_s in [0.0, -1.0, f32::NAN, f32::INFINITY] {
            let config = FleetConfig {
                speed_m_s,
                ..FleetConfig::default()
            };
            assert!(config.validate().is_err());
        }
    }

    #[test]
    fn an_error_says_which_argument_is_wrong() {
        let error = FleetError::invalid("count", "must be from 1 to 255");
        assert!(error.to_string().contains("--count"));
    }
}
