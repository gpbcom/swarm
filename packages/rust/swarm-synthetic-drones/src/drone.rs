//! The `MAVLink` state machine of one synthetic Drone.
//!
//! A [`SyntheticDrone`] receives `MAVLink` messages through [`SyntheticDrone::handle`] and moves through
//! [`SyntheticDrone::tick`]. Both write the messages they answer or emit into a vector of the caller, so that a
//! runtime can reuse one buffer for thousands of Drones. [`SyntheticDrone::tick`] allocates nothing once that vector
//! has its capacity: the mission items are stored in vectors filled once, during the upload.
//!
//! The Drone speaks a small part of the common dialect:
//!
//! - the mission protocol, with `MISSION_COUNT`, `MISSION_REQUEST_INT`, `MISSION_ITEM_INT` and `MISSION_ACK`, for the
//!   items `NAV_TAKEOFF`, `NAV_WAYPOINT` and `NAV_LAND`;
//! - `COMMAND_LONG`, answered by `COMMAND_ACK`, for arm and disarm, `MISSION_START`, `DO_PAUSE_CONTINUE`,
//!   `NAV_RETURN_TO_LAUNCH` and `NAV_LAND`;
//! - the `HEARTBEAT` of a quadrotor, and a `GLOBAL_POSITION_INT` and the `MISSION_ITEM_REACHED` of each tick.
//!
//! A message whose target system is not the Drone's own is ignored.

// The Mission upload frame is the deprecated INT variant on purpose: it is the frame a real autopilot receives.
#![allow(deprecated)]

use mavlink::dialects::common::{
    MavAutopilot, MavCmd, MavFrame, MavMessage, MavMissionResult, MavMissionType, MavModeFlag, MavResult, MavState,
    MavType, COMMAND_ACK_DATA, COMMAND_LONG_DATA, GLOBAL_POSITION_INT_DATA, HEARTBEAT_DATA, MISSION_ACK_DATA,
    MISSION_COUNT_DATA, MISSION_ITEM_INT_DATA, MISSION_ITEM_REACHED_DATA, MISSION_REQUEST_INT_DATA,
};

use crate::route::{Position, RouteFollower};

/// The most items a Mission upload may announce; a larger `MISSION_COUNT` is answered with `NO_SPACE`.
pub const MAX_MISSION_ITEMS: u16 = 1024;

/// The system id the answers are addressed to, the conventional one of a ground control station.
const GCS_SYSTEM_ID: u8 = 255;

/// The component id the answers are addressed to, which means every component.
const ALL_COMPONENTS: u8 = 0;

/// Metres per unit of a coordinate in degrees times ten million, on the Earth radius of the route module.
const METRES_PER_E7: f64 = 6_371_000.0 * std::f64::consts::PI / 180.0 / 1.0e7;

/// Heading, in centidegrees, reported while the Drone has not moved horizontally yet (`MAVLink` "unknown").
const HEADING_UNKNOWN_CDEG: u16 = u16::MAX;

/// Largest heading, in centidegrees, `MAVLink` allows (359.99 degrees).
const HEADING_MAX_CDEG: f64 = 35_999.0;

/// Horizontal speed, in metres per second, under which the heading is kept.
const HEADING_MIN_SPEED_M_S: f64 = 0.01;

/// What a synthetic Drone is built from.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct DroneConfig {
    /// The `MAVLink` system id the Drone answers to.
    pub system_id: u8,
    /// Where the Drone stands, and where it returns and lands.
    pub home: Position,
    /// The constant speed, in metres per second, of every flight.
    pub speed_m_s: f32,
}

/// What a synthetic Drone is doing.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DroneState {
    /// On the ground and disarmed.
    Landed,
    /// On the ground and armed, waiting for a Mission start.
    Armed,
    /// Flying the Mission.
    Flying,
    /// Hovering where a pause stopped it.
    Holding,
    /// Flying back to the home position, then landing.
    Returning,
    /// Descending to the ground where it is.
    Landing,
}

/// The kind of a Mission item, from its `MAVLink` command.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ItemKind {
    /// `MAV_CMD_NAV_TAKEOFF`.
    Takeoff,
    /// `MAV_CMD_NAV_WAYPOINT`.
    Waypoint,
    /// `MAV_CMD_NAV_LAND`.
    Land,
}

/// One synthetic Drone: its state, its Mission and its route follower.
#[derive(Clone, Debug)]
pub struct SyntheticDrone {
    config: DroneConfig,
    state: DroneState,
    follower: RouteFollower,
    positions: Vec<Position>,
    kinds: Vec<ItemKind>,
    expected: Option<u16>,
    elapsed_s: f64,
    cos_lat: f64,
    heading_cdeg: u16,
}

impl SyntheticDrone {
    /// A Drone landed and disarmed at `config.home`, with no Mission.
    #[must_use]
    pub fn new(config: DroneConfig) -> Self {
        Self {
            config,
            state: DroneState::Landed,
            follower: RouteFollower::new(config.home, config.speed_m_s),
            positions: Vec::new(),
            kinds: Vec::new(),
            expected: None,
            elapsed_s: 0.0,
            cos_lat: (f64::from(config.home.lat_e7) * 1.0e-7).to_radians().cos(),
            heading_cdeg: HEADING_UNKNOWN_CDEG,
        }
    }

    /// The `MAVLink` system id of the Drone.
    #[must_use]
    pub fn system_id(&self) -> u8 {
        self.config.system_id
    }

    /// What the Drone is doing.
    #[must_use]
    pub fn state(&self) -> DroneState {
        self.state
    }

    /// Where the Drone is.
    #[must_use]
    pub fn position(&self) -> Position {
        self.follower.position()
    }

    /// The `HEARTBEAT` of the Drone: a quadrotor, with the armed flag set unless it is landed.
    #[must_use]
    pub fn heartbeat(&self) -> MavMessage {
        let (base_mode, system_status) = if self.state == DroneState::Landed {
            (MavModeFlag::empty(), MavState::MAV_STATE_STANDBY)
        } else {
            (MavModeFlag::MAV_MODE_FLAG_SAFETY_ARMED, MavState::MAV_STATE_ACTIVE)
        };
        MavMessage::HEARTBEAT(HEARTBEAT_DATA {
            mavtype: MavType::MAV_TYPE_QUADROTOR,
            autopilot: MavAutopilot::MAV_AUTOPILOT_GENERIC,
            base_mode,
            system_status,
            ..Default::default()
        })
    }

    /// Handles one received message and appends the messages that answer it to `out`.
    ///
    /// A message for another system, and a message the Drone does not speak, gives no output.
    pub fn handle(&mut self, message: &MavMessage, out: &mut Vec<MavMessage>) {
        match message {
            MavMessage::MISSION_COUNT(data) if data.target_system == self.config.system_id => {
                self.on_count(data, out);
            }
            MavMessage::MISSION_ITEM_INT(data) if data.target_system == self.config.system_id => {
                self.on_item(data, out);
            }
            MavMessage::COMMAND_LONG(data) if data.target_system == self.config.system_id => {
                self.on_command(data, out);
            }
            _ => {}
        }
    }

    /// Moves the Drone for `dt_s` seconds and appends its `GLOBAL_POSITION_INT`, then the `MISSION_ITEM_REACHED`
    /// of the item reached in this step, if any, to `out`.
    ///
    /// A Drone that is not in the air stays where it is. Nothing is allocated here, apart from what `out` needs to
    /// grow when the caller did not give it capacity.
    pub fn tick(&mut self, dt_s: f32, out: &mut Vec<MavMessage>) {
        let before = self.follower.position();
        let reached = if self.is_in_the_air() && self.state != DroneState::Holding {
            self.follower.step(dt_s)
        } else {
            None
        };
        self.elapsed_s += f64::from(dt_s);
        let after = self.follower.position();
        out.push(self.position_message(before, after, dt_s));
        if let Some(index) = reached {
            self.arrive(index, out);
        }
    }

    /// Starts a Mission upload, or clears the Mission when the count is zero.
    fn on_count(&mut self, data: &MISSION_COUNT_DATA, out: &mut Vec<MavMessage>) {
        if data.mission_type != MavMissionType::MAV_MISSION_TYPE_MISSION {
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_UNSUPPORTED));
            return;
        }
        if self.is_in_the_air() {
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_DENIED));
            return;
        }
        self.clear_mission();
        if data.count > MAX_MISSION_ITEMS {
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_NO_SPACE));
            return;
        }
        if data.count == 0 {
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_ACCEPTED));
            return;
        }
        self.positions.reserve(usize::from(data.count));
        self.kinds.reserve(usize::from(data.count));
        self.expected = Some(data.count);
        out.push(Self::request(0));
    }

    /// Stores one uploaded item, then requests the next one or accepts the Mission.
    fn on_item(&mut self, data: &MISSION_ITEM_INT_DATA, out: &mut Vec<MavMessage>) {
        let Some(expected) = self.expected else {
            return;
        };
        let received = usize::from(self.next_seq());
        if usize::from(data.seq) < received {
            out.push(Self::request(self.next_seq()));
            return;
        }
        if usize::from(data.seq) > received {
            self.clear_mission();
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_INVALID_SEQUENCE));
            return;
        }
        let Some(kind) = Self::item_kind(data.command) else {
            self.clear_mission();
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_UNSUPPORTED));
            return;
        };
        let Some(position) = self.item_position(data) else {
            self.clear_mission();
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_UNSUPPORTED_FRAME));
            return;
        };
        self.positions.push(position);
        self.kinds.push(kind);
        if self.next_seq() < expected {
            out.push(Self::request(self.next_seq()));
        } else {
            self.expected = None;
            out.push(Self::mission_ack(MavMissionResult::MAV_MISSION_ACCEPTED));
        }
    }

    /// The kind of a Mission item for a `MAVLink` command, or `None` when the Drone does not support it.
    fn item_kind(command: MavCmd) -> Option<ItemKind> {
        match command {
            MavCmd::MAV_CMD_NAV_TAKEOFF => Some(ItemKind::Takeoff),
            MavCmd::MAV_CMD_NAV_WAYPOINT => Some(ItemKind::Waypoint),
            MavCmd::MAV_CMD_NAV_LAND => Some(ItemKind::Land),
            _ => None,
        }
    }

    /// The position of an item, or `None` when its frame is not supported.
    ///
    /// The altitude of a relative frame is added to the altitude of home.
    fn item_position(&self, data: &MISSION_ITEM_INT_DATA) -> Option<Position> {
        let altitude_m = match data.frame {
            MavFrame::MAV_FRAME_GLOBAL_RELATIVE_ALT_INT => self.config.home.altitude_m + data.z,
            MavFrame::MAV_FRAME_GLOBAL_INT => data.z,
            _ => return None,
        };
        Some(Position {
            lat_e7: data.x,
            lon_e7: data.y,
            altitude_m,
        })
    }

    /// The sequence number of the next item to upload.
    fn next_seq(&self) -> u16 {
        u16::try_from(self.positions.len()).unwrap_or(u16::MAX)
    }

    /// Forgets the Mission and the upload in progress.
    fn clear_mission(&mut self) {
        self.positions.clear();
        self.kinds.clear();
        self.expected = None;
    }

    /// The `MISSION_REQUEST_INT` of item `seq`.
    fn request(seq: u16) -> MavMessage {
        MavMessage::MISSION_REQUEST_INT(MISSION_REQUEST_INT_DATA {
            seq,
            target_system: GCS_SYSTEM_ID,
            target_component: ALL_COMPONENTS,
            mission_type: MavMissionType::MAV_MISSION_TYPE_MISSION,
        })
    }

    /// The `MISSION_ACK` with the given outcome.
    fn mission_ack(result: MavMissionResult) -> MavMessage {
        MavMessage::MISSION_ACK(MISSION_ACK_DATA {
            target_system: GCS_SYSTEM_ID,
            target_component: ALL_COMPONENTS,
            mavtype: result,
            mission_type: MavMissionType::MAV_MISSION_TYPE_MISSION,
            ..Default::default()
        })
    }

    /// Runs one `COMMAND_LONG` and appends its `COMMAND_ACK`.
    fn on_command(&mut self, data: &COMMAND_LONG_DATA, out: &mut Vec<MavMessage>) {
        let result = match data.command {
            MavCmd::MAV_CMD_COMPONENT_ARM_DISARM => self.arm_or_disarm(data.param1),
            MavCmd::MAV_CMD_MISSION_START => self.start_mission(),
            MavCmd::MAV_CMD_DO_PAUSE_CONTINUE => self.pause_or_continue(data.param1),
            MavCmd::MAV_CMD_NAV_RETURN_TO_LAUNCH => self.return_to_launch(),
            MavCmd::MAV_CMD_NAV_LAND => self.land(),
            _ => MavResult::MAV_RESULT_UNSUPPORTED,
        };
        out.push(MavMessage::COMMAND_ACK(COMMAND_ACK_DATA {
            command: data.command,
            result,
            target_system: GCS_SYSTEM_ID,
            target_component: ALL_COMPONENTS,
            ..Default::default()
        }));
    }

    /// Arms (`param1` of 1) or disarms (`param1` of 0) a Drone on the ground; in the air both are denied.
    fn arm_or_disarm(&mut self, param1: f32) -> MavResult {
        if !param1.is_finite() || self.is_in_the_air() {
            return MavResult::MAV_RESULT_DENIED;
        }
        self.state = if param1 >= 0.5 {
            DroneState::Armed
        } else {
            DroneState::Landed
        };
        MavResult::MAV_RESULT_ACCEPTED
    }

    /// Starts flying the Mission, which needs an armed Drone on the ground and a complete, non-empty Mission.
    fn start_mission(&mut self) -> MavResult {
        if self.state != DroneState::Armed || self.positions.is_empty() || self.expected.is_some() {
            return MavResult::MAV_RESULT_DENIED;
        }
        self.follower.set_route(&self.positions);
        self.state = DroneState::Flying;
        MavResult::MAV_RESULT_ACCEPTED
    }

    /// Holds the position (`param1` of 0) of a flying Drone, or resumes (`param1` of 1) a holding one.
    fn pause_or_continue(&mut self, param1: f32) -> MavResult {
        if !param1.is_finite() || !matches!(self.state, DroneState::Flying | DroneState::Holding) {
            return MavResult::MAV_RESULT_DENIED;
        }
        self.state = if param1 >= 0.5 {
            DroneState::Flying
        } else {
            DroneState::Holding
        };
        MavResult::MAV_RESULT_ACCEPTED
    }

    /// Flies a Drone in the air back above home, at its altitude, then lands it there.
    fn return_to_launch(&mut self) -> MavResult {
        if !matches!(self.state, DroneState::Flying | DroneState::Holding) {
            return MavResult::MAV_RESULT_DENIED;
        }
        self.begin_return();
        MavResult::MAV_RESULT_ACCEPTED
    }

    /// Lands a Drone in the air where it is.
    fn land(&mut self) -> MavResult {
        if !self.is_in_the_air() {
            return MavResult::MAV_RESULT_DENIED;
        }
        let here = self.follower.position();
        self.follower.set_route(&[Position {
            altitude_m: self.config.home.altitude_m,
            ..here
        }]);
        self.state = DroneState::Landing;
        MavResult::MAV_RESULT_ACCEPTED
    }

    /// Aims at the point above home at the current altitude, then at home itself, and becomes `Returning`.
    fn begin_return(&mut self) {
        let here = self.follower.position();
        let above_home = Position {
            altitude_m: here.altitude_m,
            ..self.config.home
        };
        self.follower.set_route(&[above_home, self.config.home]);
        self.state = DroneState::Returning;
    }

    /// Whether the Drone is not on the ground.
    fn is_in_the_air(&self) -> bool {
        !matches!(self.state, DroneState::Landed | DroneState::Armed)
    }

    /// Applies the arrival at waypoint `index` of the route being flown.
    fn arrive(&mut self, index: usize, out: &mut Vec<MavMessage>) {
        match self.state {
            DroneState::Flying => {
                out.push(MavMessage::MISSION_ITEM_REACHED(MISSION_ITEM_REACHED_DATA {
                    seq: u16::try_from(index).unwrap_or(u16::MAX),
                }));
                if self.kinds.get(index) == Some(&ItemKind::Land) {
                    self.state = DroneState::Landed;
                } else if self.follower.is_complete() {
                    self.begin_return();
                }
            }
            DroneState::Returning | DroneState::Landing => {
                if self.follower.is_complete() {
                    self.state = DroneState::Landed;
                }
            }
            DroneState::Landed | DroneState::Armed | DroneState::Holding => {}
        }
    }

    /// The `GLOBAL_POSITION_INT` of the Drone after a step of `dt_s` seconds that moved it from `before` to `after`.
    #[allow(clippy::cast_possible_truncation, clippy::cast_sign_loss)]
    fn position_message(&mut self, before: Position, after: Position, dt_s: f32) -> MavMessage {
        let (north_m_s, east_m_s, up_m_s) = if dt_s > 0.0 {
            let dt = f64::from(dt_s);
            (
                (f64::from(after.lat_e7) - f64::from(before.lat_e7)) * METRES_PER_E7 / dt,
                (f64::from(after.lon_e7) - f64::from(before.lon_e7)) * METRES_PER_E7 * self.cos_lat / dt,
                f64::from(after.altitude_m - before.altitude_m) / dt,
            )
        } else {
            (0.0, 0.0, 0.0)
        };
        if north_m_s.hypot(east_m_s) > HEADING_MIN_SPEED_M_S {
            let degrees = east_m_s.atan2(north_m_s).to_degrees().rem_euclid(360.0);
            self.heading_cdeg = (degrees * 100.0).round().min(HEADING_MAX_CDEG) as u16;
        }
        MavMessage::GLOBAL_POSITION_INT(GLOBAL_POSITION_INT_DATA {
            time_boot_ms: (self.elapsed_s * 1000.0) as u32,
            lat: after.lat_e7,
            lon: after.lon_e7,
            alt: (after.altitude_m * 1000.0) as i32,
            relative_alt: ((after.altitude_m - self.config.home.altitude_m) * 1000.0) as i32,
            vx: Self::centimetres_per_second(north_m_s),
            vy: Self::centimetres_per_second(east_m_s),
            vz: Self::centimetres_per_second(-up_m_s),
            hdg: self.heading_cdeg,
        })
    }

    /// A speed in metres per second as centimetres per second, saturated to the range of `MAVLink`'s `int16`.
    #[allow(clippy::cast_possible_truncation)]
    fn centimetres_per_second(speed_m_s: f64) -> i16 {
        (speed_m_s * 100.0)
            .round()
            .clamp(f64::from(i16::MIN), f64::from(i16::MAX)) as i16
    }
}
